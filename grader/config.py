import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class Mode(Enum):
    COMPLETION = 1
    RUNNABLE = 2
    CORRECTNESS = 3

class Config:
    CHECKPOINT_QUESTION_TAG = "# @@@"
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    GRADER_MODE = Mode.CORRECTNESS
