import os
from supabase import create_client, Client
from app import check_user_in_database, update_github_link_db, get_github_link_db

import pytz  
from datetime import datetime



time_stamp = datetime.now(pytz.timezone('US/Eastern')).isoformat()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Delete everything in the table
response = supabase.from_('Users').delete().neq('email', '').execute()
response = supabase.from_('Tutorial_Submission').delete().neq('email','').execute()

# Check the response
print(response)