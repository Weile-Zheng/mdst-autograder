import os
from flask import Flask, redirect, url_for, request, session, render_template, flash
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    user = session.get('user')
    if not user: return redirect(url_for("login"))
    check_user_in_database(user["id"], user["user_full_name"], user["user_email"])
    return render_template('index.html', user=user)

@app.route('/login/')
def login():
    user = session.get('user')
    if user: return redirect(url_for("home"))
    return render_template('login.html')

@app.route('/login/auth/')
def login_auth():
    callback_url = url_for('callback', _external=True) 
    response = supabase.auth.sign_in_with_oauth({"provider": 'google', 
    "options": {"redirect_to": callback_url}})
    
    return redirect(response.url)

@app.route('/callback/')
def callback():
    return render_template('callback.html')

@app.route('/store_token/', methods=['POST'])
def store_token():
    access_token = request.form.get('access_token')

    if access_token:
        session['access_token'] = access_token
        user_info = supabase.auth.get_user(access_token).user
        user_info_dict = {
            'id':user_info.id,
            'user_full_name': user_info.user_metadata['full_name'],
            'user_email':user_info.user_metadata['email'],
            'user_picture': user_info.user_metadata['picture'] #picture url
        }
        print(user_info_dict)
        session["user"]=user_info_dict
        return redirect(url_for('home'))
    else:
        return "Error: Access token not found", 400

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/submit_github_link/', methods=['POST'])
def submit_github_link():
    github_link = request.form.get('github_link')
    flash('GitHub link submitted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/upload_checkpoint_files/', methods=['POST'])
def upload_checkpoint_files():
    files = request.files.getlist('checkpoint_files')
    flash('Files uploaded successfully!', 'success')
    return redirect(url_for('home'))

######################################################
# Helper functions
######################################################

def check_user_in_database(uid: str, full_name: str, email):
    """
    Check if user is in database. If not add user to database
    """
    response = supabase.from_('Users').select('google_id').eq('google_id', uid).execute()
    
    if not response.data:
        supabase.from_('Users').insert({
                'google_id': uid,
                'full_name': full_name,
                'email': email,
            }).execute()

        return redirect(url_for('home'))
    else:
        return "Error: Access token not found", 400


    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)