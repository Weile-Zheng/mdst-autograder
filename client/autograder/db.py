import requests
import pytz
from datetime import datetime
from autograder import supabase_client 

######################################################
# Helper functions
######################################################
def check_user_in_database(uid: str, full_name: str, email) -> str:
    """
    Check if user is in database. If not add user to database in Users table with 
    google_id and create entry in the tutorial submission table with null values. 
    """
    response = supabase_client.table('Users').select('google_id').eq('google_id', uid).execute()
    
    if not response.data:
        
        # Make an empty entry in tutorial submission table:
        # This empty entry would simplify our job when updating scores,
        # as we do note need to check for existance of an entry to update in tutorial
        # submission, it is all taken care of during user first time log in. 
        supabase_client.table('Tutorial_Submission').insert({
            'email': email
        }).execute()
        print("Submission entry created in table: Submission")

        # Make an entry in users table
        supabase_client.table('Users').insert({
                'google_id': uid,
                'full_name': full_name,
                'email': email,
            }).execute()
        print("User enry created in table: Users")

    else:
        return "Error: Access token not found", 400

def update_github_link_db(uid: str, github_link: str) -> None:
    """
    Given uid(google id), update github link for the user on Users table
    """
    supabase_client.table('Users').update({'github_link': github_link}).eq('google_id', uid).execute()


def get_github_link_db(uid:str) -> str:
    """
    Get github link for te user on Users table

        @params
            uid: google_id
    """
    response = supabase_client.table('Users').select('github_link').eq('google_id', uid).execute()
    if response.data:
        return response.data[0]['github_link']

def update_checkpoint_submission_db(email: str, 
        checkpoint_file_name: str, isCheckpoint0: bool) -> str:
    """
    Update the Tutorials Submission table. Return time stamp of the tutorial submission
    """
    time_stamp = datetime.now(pytz.timezone('US/Eastern')).isoformat()
    if isCheckpoint0:
        supabase_client.table('Tutorial_Submission').update({
             'checkpoint0_filename': checkpoint_file_name,
             'checkpoint0_last_submission_time': time_stamp,
            }).eq('email', email).execute()
    else:
        supabase_client.table('Tutorial_Submission').update({
            'checkpoint1_filename': checkpoint_file_name, 
            'checkpoint1_last_submission_time': time_stamp,
            }).eq('email', email).execute()
    return time_stamp

def get_checkpoint_submission_db(email: str) -> list[str]:
    """
    Get checkpoint submission data for the user from Tutorial_Submission table
    """
    response = supabase_client.table(
        'Tutorial_Submission').select('checkpoint0_filename, checkpoint0_last_submission_time,checkpoint1_filename, checkpoint1_last_submission_time').eq('email', email).execute()
    if response.data:
        return response.data[0]

def upload_checkpoint_to_supabase(filename: str, filepath: str) -> requests.Response: 
    """
    Upload a checkpoint file to supabase bucket: "checkpoints".

    If file name already exist in bucket, override. 

    Note this function expects a valid input and does not do additial checkings 
    on the file type, size etc. 
    """
    return supabase_client.storage.from_('checkpoints').upload(filename, filepath, {'upsert':'true'})

def get_checkpoint_file_url(filename: str, bucketname: str) -> str:
    """
    Get the url of the file in the checkpoint bucket
    """
    # 60 days in seconds
    expiration_time = 60 * 24 * 60 * 60
    signed_url = supabase_client.storage.from_(bucketname).create_signed_url(filename, expiration_time)['signedURL']
    return f"{signed_url}&download={filename}"
    