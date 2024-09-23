import os
from dotenv import load_dotenv

load_dotenv()

class Config: 
    SECRET_KEY = os.getenv('SECRET_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 500 * 1024  # 500 KB for checkpoint files
    ALLOWED_FILENAMES = {'checkpoint0.ipynb', 'checkpoint1.ipynb'}
    TIMEZONE = 'US/Eastern'