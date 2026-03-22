# User Acceptance Tests (UAT)

## Scenario 1: Initial Recommendation
- **GIVEN**: A new user has registered and set their language to 'English'.
- **WHEN**: The user sends the `/recommend` command.
- **THEN**: The bot should return a classic English poem that the user hasn't seen before.
- **Status**: ✅ Passed

## Scenario 2: Voice Recitation Check
- **GIVEN**: A user is reviewing a poem and chooses 'Voice Check'.
- **WHEN**: The user uploads a voice message reciting the first stanza.
- **THEN**: The backend should process the audio via Vosk and return an accuracy score (0-100%).
- **Status**: ✅ Passed

## Scenario 3: Spaced Repetition Scheduling
- **GIVEN**: A user has just finished reviewing a poem with a high score (5).
- **WHEN**: The system updates the memorization record.
- **THEN**: The next review date should be scheduled further in the future according to the SM-2 algorithm.
- **Status**: ✅ Passed

## Results Summary
All core UAT scenarios for MVP v2.5 are passing. Minor UX feedback regarding voice message duration limits has been addressed.
