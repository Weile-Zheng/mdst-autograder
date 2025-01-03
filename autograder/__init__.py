# __init__.py
import os 
from flask import Flask
from supabase import create_client
from autograder.config import Config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=BASE_DIR / "templates")
app.config.from_object(Config)

supabase_client = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

import autograder.routes # Register the routes