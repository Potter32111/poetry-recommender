#!/bin/bash

declare -a issues=(
  # User Stories (MVP)
  "[Feature] Register and Preferences|As a new user, I want to start the bot using /start"
  "[Feature] Poem Recommendation|As a user, I want to receive a personalized poem recommendation"
  "[Feature] Add to Learning List|As a user, I want to add a recommended poem to my learning list"
  "[Feature] SM-2 Spaced Repetition|As a student, I want to use the SM-2 algorithm for learning"
  "[Feature] Voice Recitation|As a user, I want to recite a poem via voice message"
  "[Feature] Accuracy Score|As a user, I want to see an accuracy score after reciting"
  "[Feature] Manual Rating|As a user, I want to manually rate my recall (0-5)"
  "[Feature] Daily Reminders|As a user, I want to receive daily reminders for due reviews"
  "[Feature] Gamification|As a competitive user, I want to earn XP and level up"
  "[Feature] Progress Dashboard|As a user, I want to view my progress dashboard"
  "[Feature] Learning Streak|As a user, I want to maintain a streak of consecutive days"
  "[Feature] Search Poems|As a user, I want to search for poems by author or title"

  # Technical Tasks
  "[Infra] Docker Deployment|Deploy the system using Docker Compose"
  "[DB] Secure Storage|Store user data securely in PostgreSQL"
  "[DB] Seed Data|Seed the database with initial poems"
  "[QA] Implement Unit Tests|Write 5 rigorous unit tests for SM-2 and difflib"
  "[QA] Implement Integration Tests|Write 5 integration tests mocking FastAPI"
  "[CI/CD] GitHub Actions|Set up CI pipeline with Ruff and Pytest"
  "[Docs] PlantUML Architecture Diagrams|Component, Sequence, and Deployment diagrams"
  "[Docs] GitHub Templates|Issue and PR markdown templates"

  # UX Polishing
  "[Feature] Leaderboard|Endpoint to show top 10 users ranked by Level and XP"
  "[UX] Seamless Review Flow|Next Poem button after scoring"
  "[UX] Save for Later Button|Save recommended poem without learning immediately"
  "[UX] Translate Button|Translate English poems to Russian"
  "[Feature] Stanza-by-Stanza Mode|Learning mode that breaks long poems into chunks"

  # Bugs / Feedback
  "[Docs/Fix] Troubleshooting OGG Audio|Document ffmpeg errors for Voice evaluation"
  "[Docs/Fix] Safe Alembic Migrations|Document how to run Alembic safely"
)

echo "Creating issues using GitHub CLI (gh)..."

for issue in "${issues[@]}"; do
    title="${issue%%|*}"
    body="${issue#*|}"
    
    # Identify label by prefix
    label="enhancement"
    if [[ $title == *"[QA]"* ]]; then label="testing"; fi
    if [[ $title == *"[Docs]"* ]]; then label="documentation"; fi
    if [[ $title == *"[Bug]"* ]] || [[ $title == *"[Fix]"* ]]; then label="bug"; fi
    
    gh issue create --title "$title" --body "$body" --label "$label"
    echo "Created: $title"
    sleep 2 # Prevent GitHub API rate limiting
done

echo "Done! All issues have been created."
