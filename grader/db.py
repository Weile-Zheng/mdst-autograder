from config import Config
from supabase import create_client

supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def upload_score(email: str, checkpoint: int, raw: int, percent: float) -> bool:
    """
    Upload the score to the Supabase database. Return True if successful.

    Args:
        email (str): The email of the user.
        checkpoint_file_name (str): The filename of the checkpoint file.
        isCheckpoint0 (bool): Whether the checkpoint is the first checkpoint.
        raw (int): The raw score of the user.
        percent (float): The percentage score of the user.
    """
    try:
        if checkpoint == 0:
            supabase_client.table('Tutorial_Submission').update({
                'checkpoint0_raw': raw,
                'checkpoint0_percent': percent,
            }).eq('email', email).execute()
        else:
            supabase_client.table('Tutorial_Submission').update({
                'checkpoint1_raw': raw,
                'checkpoint1_percent': percent,
            }).eq('email', email).execute()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False