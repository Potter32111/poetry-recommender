import asyncio
import os
import sys

# Add backend directory to sys.path so we can import app modules
# However, this script will run outside Docker, so we need vosk manually installed
# Actually, since it's hard to get vosk running locally on Windows without matching Python versions,
# Let's just create a test route in FastAPI that logs the transcript loudly
