"""Canonical pipeline orchestrator coordinating wake, VAD, STT, Groq, TTS, and visuals."""

import logging
from collections.abc import AsyncIterator
from typing import Any

from aria.core.audio.analyzer import AudioAnalyzer
from aria.core.audio.player import AudioPlayerBridge
from aria.core.intent.directioner_client import (
    DIRECTIONER_TOOL_DEFINITION,
    DirectionerAIClient,
)
from aria.core.llm.base import LLMClient
from aria.core.memory.long_term import LongTermMemory
from aria.core.memory.session import SessionMemory
from aria.core.pipeline.events import (
    EventBus,
    LLMTokenEvent,
    StateTransitionEvent,
    STTTranscriptEvent,
    TTSAudioChunkEvent,
    VADStateChangedEvent,
    WakeWordDetectedEvent,
)
from aria.core.pipeline.state import AssistantMode, PipelineState
from aria.core.stt.base import StreamingSTT
from aria.core.tts.base import StreamingTTS
from aria.core.vad.base import VADDetector
from aria.core.wake.base import WakeWordDetector
from aria.visual.overlay.state_machine import VisualStateMachine

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Coordinates the full end-to-end Aria voice loop adhering strictly to canonical order."""

    def __init__(
        self,
        wake_detector: WakeWordDetector,
        vad_detector: VADDetector,
        stt_client: StreamingSTT,
        llm_client: LLMClient,
        tts_client: StreamingTTS,
        audio_analyzer: AudioAnalyzer | None = None,
        session_memory: SessionMemory | None = None,
        long_term_memory: LongTermMemory | None = None,
        directioner_client: DirectionerAIClient | None = None,
        visual_state_machine: VisualStateMachine | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.wake_detector = wake_detector
        self.vad_detector = vad_detector
        self.stt_client = stt_client
        self.llm_client = llm_client
        self.tts_client = tts_client

        self.audio_analyzer = audio_analyzer or AudioAnalyzer()
        self.session_memory = session_memory or SessionMemory()
        self.long_term_memory = long_term_memory or LongTermMemory()
        self.directioner_client = directioner_client or DirectionerAIClient()
        self.visual_state_machine = visual_state_machine or VisualStateMachine()
        self.event_bus = event_bus or EventBus()

        self.audio_player = AudioPlayerBridge(
            analyzer=self.audio_analyzer,
            on_metrics=self._handle_audio_metrics,
        )

        self._current_state = PipelineState.IDLE
        self._current_mode = AssistantMode.ARIA
        self._is_running = False

    @property
    def current_state(self) -> PipelineState:
        """Current pipeline state."""
        return self._current_state

    @property
    def current_mode(self) -> AssistantMode:
        """Current assistant personality mode."""
        return self._current_mode

    async def transition_state(self, new_state: PipelineState) -> None:
        """Transition pipeline state, notify visual state machine, and emit event."""
        if self._current_state != new_state:
            prev_state = self._current_state
            self._current_state = new_state
            self.visual_state_machine.transition_state(new_state)
            await self.event_bus.emit(
                StateTransitionEvent(
                    previous_state=prev_state,
                    current_state=new_state,
                    mode=self._current_mode,
                )
            )

    async def set_mode(self, mode: AssistantMode) -> None:
        """Switch persona mode and trigger visual transformation."""
        if self._current_mode != mode:
            self._current_mode = mode
            self.session_memory.set_mode(mode)
            self.visual_state_machine.trigger_mode_transformation(mode)

    def _handle_audio_metrics(self, metrics: Any) -> None:
        """Callback from audio analyzer to update visual reactivity."""
        self.visual_state_machine.update_audio_reactivity(metrics)

    async def process_microphone_frame(self, audio_frame: bytes) -> None:
        """Process incoming 16-bit PCM audio frame through wake detection."""
        if self._current_state == PipelineState.IDLE:
            wake_result = self.wake_detector.process_frame(audio_frame)
            if wake_result:
                logger.info(
                    "Wake word detected: %s (confidence: %.2f)",
                    wake_result.name,
                    wake_result.confidence,
                )
                await self.set_mode(wake_result.mode)
                await self.event_bus.emit(
                    WakeWordDetectedEvent(
                        wake_word=wake_result.name,
                        mode=wake_result.mode,
                        confidence=wake_result.confidence,
                    )
                )
                await self.transition_state(PipelineState.LISTENING)

    async def run_voice_turn(
        self,
        audio_stream: AsyncIterator[bytes],
    ) -> str:
        """Execute a full conversational voice loop turn from audio stream to speech output.

        Canonical Order:
        1. Wake Word (checked before or during stream)
        2. Silero VAD (accumulate speech until end-of-utterance)
        3. smallest.ai STT (stream audio, receive final transcript)
        4. Groq Reasoning (inject system prompt + memory + tools)
        5. smallest.ai TTS (stream speech audio chunks)
        6. Audio Analysis & Visual Update
        """
        await self.transition_state(PipelineState.LISTENING)
        await self.stt_client.connect()

        stt_final_text = ""
        speech_bytes_buffer = bytearray()

        # Step 2: VAD & Step 3: STT Streaming
        async for frame in audio_stream:
            vad_decision = self.vad_detector.process_frame(frame)
            await self.event_bus.emit(
                VADStateChangedEvent(
                    is_speech=vad_decision.is_speech,
                    speech_duration_ms=vad_decision.speech_duration_ms,
                )
            )

            if vad_decision.is_speech or vad_decision.speech_duration_ms > 0:
                speech_bytes_buffer.extend(frame)
                await self.stt_client.send_audio(frame)

            if vad_decision.is_end_of_utterance:
                logger.info("End of utterance detected by VAD.")
                break

        await self.stt_client.finish_stream()

        async for stt_result in self.stt_client.receive_transcripts():
            await self.event_bus.emit(
                STTTranscriptEvent(
                    text=stt_result.text,
                    is_final=stt_result.is_final,
                    confidence=stt_result.confidence,
                )
            )
            if stt_result.is_final:
                stt_final_text = stt_result.text

        await self.stt_client.close()

        if not stt_final_text:
            logger.info("No speech detected in turn. Returning to IDLE.")
            await self.transition_state(PipelineState.IDLE)
            return ""

        logger.info("Final STT transcript: '%s'", stt_final_text)

        # Step 4: Groq Reasoning & Memory Integration
        from aria.core.llm.personality_matrix import get_system_prompt

        await self.transition_state(PipelineState.THINKING)
        self.session_memory.add_turn(role="user", content=stt_final_text)
        self.long_term_memory.save_turn(
            session_id=self.session_memory.session_id,
            mode=self._current_mode,
            role="user",
            content=stt_final_text,
        )

        memory_facts = self.long_term_memory.get_all_facts()
        system_prompt = get_system_prompt(
            mode=self._current_mode,
            memory_context=self.session_memory.get_recent_context_summary(),
            active_panels=self.session_memory.active_panels,
            extra_facts=memory_facts,
        )

        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.session_memory.get_messages_for_llm()

        # Step 4: Groq Token Stream & Step 5: smallest.ai TTS Stream
        async def token_generator() -> AsyncIterator[str]:
            full_response_text = []
            async for chunk in self.llm_client.stream_chat(
                messages=messages,
                tools=[DIRECTIONER_TOOL_DEFINITION],
            ):
                if chunk.tool_calls:
                    # Directioner AI boundary delegation
                    for tc in chunk.tool_calls:
                        if tc.tool_name == "delegate_to_directioner_ai":
                            await self.transition_state(PipelineState.DELEGATING)
                            intent = self.directioner_client.build_intent_from_tool_call(
                                tc.arguments_json
                            )
                            if intent.requires_confirmation:
                                await self.transition_state(PipelineState.CONFIRMATION_REQUIRED)
                            result = await self.directioner_client.execute_intent(
                                intent, confirmed_by_user=True
                            )
                            msg = result.output.get("message", "Action completed.")
                            yield msg
                            full_response_text.append(msg)
                elif chunk.text:
                    await self.event_bus.emit(
                        LLMTokenEvent(
                            token=chunk.text,
                            is_first_token=chunk.is_first_token,
                            is_complete=chunk.is_complete,
                        )
                    )
                    full_response_text.append(chunk.text)
                    yield chunk.text

        await self.transition_state(PipelineState.SPEAKING)

        spoken_tokens: list[str] = []

        async def tracked_token_stream() -> AsyncIterator[str]:
            async for token in token_generator():
                spoken_tokens.append(token)
                yield token

        # Step 5: TTS Speech generation & Step 6: Audio analysis
        async for audio_chunk in self.tts_client.stream_speech(tracked_token_stream()):
            if audio_chunk.audio_bytes:
                await self.event_bus.emit(
                    TTSAudioChunkEvent(
                        audio_bytes=audio_chunk.audio_bytes,
                        sample_rate=audio_chunk.sample_rate,
                        is_first_chunk=audio_chunk.is_first_chunk,
                        is_final_chunk=audio_chunk.is_final_chunk,
                    )
                )
                await self.audio_player.play_chunk(audio_chunk.audio_bytes)

        full_assistant_reply = "".join(spoken_tokens)
        self.session_memory.add_turn(role="assistant", content=full_assistant_reply)
        self.long_term_memory.save_turn(
            session_id=self.session_memory.session_id,
            mode=self._current_mode,
            role="assistant",
            content=full_assistant_reply,
        )

        await self.transition_state(PipelineState.IDLE)
        return full_assistant_reply
