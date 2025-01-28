import os
import pytz
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Config: 
    SECRET_KEY = os.getenv('SECRET_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 500 * 1024  # 500 KB for checkpoint files
    ALLOWED_FILENAMES = {'checkpoint0.ipynb', 'checkpoint1.ipynb'}
    TIMEZONE = 'US/Eastern'
    
    MQ_PRIMARY = os.getenv('SERVICEBUS_PRIMARY_STRING') # Azure Service Bus primary connection string
    MQ_NAME = os.getenv('SERVICEBUS_QUEUE_NAME') # Azure Service Bus queue name
    
    CHECKPOINT_QUESTION_TAG = "# @@@"
    DEADLINE = datetime(2025, 1, 24, 23, 59, tzinfo=pytz.timezone('US/Eastern'))