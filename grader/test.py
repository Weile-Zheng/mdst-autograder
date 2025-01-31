import os
import json
from grader import run_checkpoint_tests
from db import upload_score
from util import download_checkpoint, Message

if __name__ == "__main__":
    msg = {"email": "weilez@umich.edu", "checkpoint": 0, "url": "https://ztabaafahvxlvhoejunj.supabase.co/storage/v1/object/sign/checkpoints/weilez_checkpoint0.ipynb?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGVja3BvaW50cy93ZWlsZXpfY2hlY2twb2ludDAuaXB5bmIiLCJpYXQiOjE3MzgyOTYxMjMsImV4cCI6MTc0MzQ4MDEyM30.jCMUdPOj1ekkfrmY9bkOSL99h7T8Tiw_ClRSHKMXMXk&download=weilez_checkpoint0.ipynb"}
    
    msg_obj = Message.from_json(json.dumps(msg))
    email, checkpoint, url = msg_obj.email, msg_obj.checkpoint, msg_obj.url
    temp_file = f"checkpoint{checkpoint}.ipynb"

    print("Downloading checkpoint file from URL.")
    download_checkpoint(url, name=temp_file)

    print("Running checkpoint tests.")
    result = run_checkpoint_tests(temp_file)

    print("Uploading score to database.")
    success = upload_score(email, checkpoint, result["raw_score"], result["percent_score"])

    if success:
        print("Score uploaded successfully, cleaning up.")
        os.remove(temp_file)
    else: 
        print("Error uploading score to database.")
        raise Exception("Error uploading score to database.")
