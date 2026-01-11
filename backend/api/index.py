import sys
import os

# Add the backend directory to sys.path to allow imports from data_utils and llm_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# This is the entry point for Vercel's serverless runtime
# It exports the FastAPI app instance for routing.
