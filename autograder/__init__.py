# __init__.py
from flask import Flask
from supabase import create_client
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

supabase_client = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

import routes # Register the routes