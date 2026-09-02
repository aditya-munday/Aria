# Design Decision 002: Long-Term Memory Growth & Eviction Policy

**Status:** APPROVED / IMPLEMENTED IN SCHEMA  
**Category:** Data Architecture & Privacy  
**Author:** Aria Lead Engineer Agent  
**Date:** 2026-09-02  

---

## 1. Context & Problem Statement
The Aria architecture incorporates SQLite for session memory (short-term turn context) and long-term memory (user preferences, facts, conversational history). 

Without an explicit growth, retention, and eviction policy, local SQLite storage could grow indefinitely on user machines, creating privacy leaks, index degradation, and unbounded disk consumption.

---

## 2. Policy Specifications

### A. Memory Tiers & Storage Bounds

1. **Session Memory (`session_turns` table):**
   - **Scope:** Ephemeral conversation buffer within active wake session.
   - **Policy:** Maximum **50 turns** per session in memory/cache; active session turns archived to history upon session timeout (inactivity > 5 minutes).
   - **Retention:** Active session cleaned on app restart.

2. **Conversation History (`conversation_history` table):**
   - **Scope:** Past interactions for context retrieval.
   - **Retention Bound:** Rolling **90-day retention window** OR maximum **5,000 recorded interactions** (configurable by user in Settings companion).
   - **Eviction Strategy:** Automatic FIFO (First-In, First-Out) prune triggered upon database connection when exceeding threshold:
     ```sql
     DELETE FROM conversation_history 
     WHERE id NOT IN (
         SELECT id FROM conversation_history ORDER BY created_at DESC LIMIT 5000
     );
     ```

3. **User Preferences & Facts (`user_facts` & `preferences` tables):**
   - **Scope:** Key-value preferences, voice traits, and user-explicit facts.
   - **Retention Bound:** Uncapped by time, but capped by count at **1,000 active facts** with LRU (Least Recently Used) access timestamp tracking.
   - **Privacy Wipe:** One-call SQLite transaction `CLEAR_ALL_MEMORY` for immediate user privacy compliance.

4. **Performance & Compaction:**
   - Automatic `PRAGMA incremental_vacuum` executed on database close or during idle maintenance when free page count exceeds 10MB.

---

## 3. Summary of Guarantees
- Local database disk footprint is strictly bounded (capped to ~50MB nominal storage limit).
- Privacy controls allow selective or full zero-trace purges.
- Eviction runs asynchronously during non-interactive idle state or startup.
