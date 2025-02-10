import logging
import os
import random
import azure.functions as func
from grader import run_checkpoint_tests
from testgroq import run_check
from db import upload_score
from util import download_checkpoint, Message
from config import Config

app = func.FunctionApp()


@app.function_name(name="ServiceBusQueueTrigger1")

@app.service_bus_queue_trigger(arg_name="msg", 
                            queue_name="grade-queue", 
                            connection="CONNECTION_STRING")

def process_grading_job(msg: func.ServiceBusMessage):
    logging.info('New grading job received from message queue.')
    
    msg_obj = Message.from_json(msg.get_body().decode('utf-8'))
    email, checkpoint, url = msg_obj.email, msg_obj.checkpoint, msg_obj.url
    unique_id = str(random.randint(1000, 9999))
    temp_file = f"checkpoint{checkpoint}_{email}_{unique_id}.ipynb"

    logging.info("Downloading checkpoint file from URL.")
    download_checkpoint(url, name=temp_file)

    logging.info("Running checkpoint tests.")
    raw_score, percent_score = run_check(temp_file, Config.CHECKPOINT_QUESTION_TAG, Config.GRADER_MODE)

    logging.info("Uploading score to database.")
    success = upload_score(email, checkpoint, raw_score, percent_score)

    if success:
        logging.info("Score uploaded successfully, cleaning up.")
        os.remove(temp_file)
    else: 
        logging.error("Error uploading score to database.")
        raise Exception("Error uploading score to database.")
    