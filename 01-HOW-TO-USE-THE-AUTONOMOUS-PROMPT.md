# How to Use the Autonomous Starting Prompt

## Quick Start

1. Create a new chat with a capable coding agent (Grok, Claude, Cursor Agent, Aider, OpenHands, Devin, etc.).
2. Copy the **entire contents** of `prompts/00-AUTONOMOUS-STARTING-PROMPT.md`.
3. Paste it as the first message.
4. (Optional but recommended) Immediately after, paste any repository URLs you want the agent to study, for example:

   ```
   Study these repositories for patterns:
   - https://github.com/example/jarvis-hud
   - https://github.com/example/voice-pipeline
   - ...
   ```

5. The agent is instructed to begin immediately and keep working until a usable core loop exists.

## What the Agent Will Do

- Create GitHub issues for every major piece of work
- Work on feature branches
- Open Pull Requests
- Keep CI (GitHub Actions) as the only place real execution happens
- Respect the locked vision documents
- Follow the mandatory pipeline:  
  **openWakeWord → Silero VAD → smallest.ai STT → Grok (system prompts + DB) → smallest.ai TTS (+ vision interface)**

## Important

- Do **not** edit the three original documents (`01-`, `02-`, `03-`).
- The agent is allowed (and expected) to create new files under `architecture/`, `prompts/`, `.github/`, source code directories, etc.
- All real testing and building must go through GitHub Actions.

## After the First Run

You can continue the same chat or start a new one with a short follow-up:

```
Continue from the current state of the repository. 
Still follow the autonomous rules. 
Current priority: <whatever is next>
```

The agent already knows the full rules from the master prompt.
