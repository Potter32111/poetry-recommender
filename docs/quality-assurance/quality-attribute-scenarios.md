# Quality Attribute Scenarios (ISO 25010)

This document outlines the quality attribute scenarios for the Poetry Recommender system, following the ISO 25010 standard.

## 1. Maintainability (Modularity)
**Scenario:** A developer needs to swap the current STT engine (Vosk) for another one (e.g., OpenAI Whisper).
- **Source:** Developer
- **Stimulus:** Request to change the speech-to-text implementation.
- **Environment:** Development time.
- **Artifact:** `backend/app/services/voice_evaluator.py`.
- **Response:** The change should be isolated to the `transcribe` and `convert_ogg_to_wav` functions or a new service implementation without affecting the comparison logic or the API endpoints.
- **Measure:** Change is completed within 4 hours without modifying more than 1 file.

## 2. Performance Efficiency (Time Behavior)
**Scenario:** A user sends a 15-second voice message for poem recitation checking.
- **Source:** User
- **Stimulus:** Voice message sent to the bot.
- **Environment:** Normal operation (Production).
- **Artifact:** Backend Voice Evaluation Service.
- **Response:** The system converts the audio, transcribes it, and provides feedback.
- **Measure:** Total response time (from bot receiving voice to user receiving feedback) is under 10 seconds.

## 3. Reliability (Recoverability)
**Scenario:** The backend service crashes while processing a voice message due to memory exhaustion by the ML model.
- **Source:** System
- **Stimulus:** Service crash.
- **Environment:** Production.
- **Artifact:** Docker / Kubernetes (Deployment).
- **Response:** The container orchestrator detects the failure and restarts the container.
- **Measure:** Service is back online within 30 seconds; state is maintained in the database.
