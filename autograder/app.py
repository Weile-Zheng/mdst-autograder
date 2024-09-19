from flask import Flask, redirect, render_template, request, session, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    response = supabase.auth.sign_in_with_oauth({"provider": 'google', "redirect_to": url_for('callback', _external=True)})
    return redirect(response.url)

@app.route('/callback')
def callback():
    # Get the OAuth token from the query parameters
    token = request.args.get('access_token')
    if token:
        # Use the token to get user information from Supabase
        user_info = supabase.auth.api.get_user(token)
        if user_info:
            session['user'] = user_info
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)