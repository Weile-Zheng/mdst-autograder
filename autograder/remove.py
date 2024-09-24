import os
from supabase import create_client, Client
from app import check_user_in_database, update_github_link_db, get_github_link_db

import pytz  
from datetime import datetime


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


"""
Delete all entries from Users and Tutorial_Submission table. For testing purposes only. 
"""
response0 = supabase.from_('Users').delete().neq('email', '').execute()
response1 = supabase.from_('Tutorial_Submission').delete().neq('email','').execute()

print(response0)
print(response1)