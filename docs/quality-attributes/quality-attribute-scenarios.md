# Quality Attribute Scenarios (ISO 25010)

## ⚡ Performance Efficiency
### 🚀 Time Behavior
- **Importance**: Users expect near-instant feedback when reciting poems.
- **Scenario**: A user sends a 10-second voice message for verification.
- **Test**: Measure the time from message upload to score receipt.
- **Requirement**: Processing must complete within < 3 seconds on standard VPS hardware.
- **Execution**: Automated performance tests using `locust` or manual timing during UAT.

## 🛡️ Reliability
### 🔄 Recoverability
- **Importance**: Memorization progress is valuable; data loss must be prevented.
- **Scenario**: The backend container crashes during a database write.
- **Test**: Force-stop the container during an active session and verify data consistency upon restart.
- **Requirement**: PostgreSQL transactions must ensure no partial data is committed.
- **Execution**: Manual fault injection in the dev environment.

## 🎨 Usability
### ♿ Accessibility
- **Importance**: The bot should be usable by people with different linguistic backgrounds.
- **Scenario**: A user with a strong accent recites a poem.
- **Test**: Verify that the fuzzy matching algorithm accounts for minor STT errors.
- **Requirement**: Similarity threshold should be adjustable (currently 80%).
- **Execution**: Testing with diverse voice samples.
