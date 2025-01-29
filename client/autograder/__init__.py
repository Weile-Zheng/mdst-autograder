# __init__.py
from flask import Flask
from supabase import create_client
from autograder.mq import MQ
from autograder.config import Config

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

queue_sender = MQ(app.config["MQ_PRIMARY"], app.config["MQ_NAME"])
supabase_client = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

import autograder.routes # Register the routes