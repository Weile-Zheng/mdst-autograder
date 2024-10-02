import os
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


"""
Delete all entries from Users and Tutorial_Submission table. For testing purposes only. 
"""
response0 = supabase.table('Users').delete().neq('email', '').execute()
response1 = supabase.table('Tutorial_Submission').delete().neq('email','').execute()

print(response0)
print(response1)