#----Utils
import os, requests
import pytz  
from datetime import datetime

#----Flask
from flask import Flask, redirect, url_for, request, session, render_template, flash
from werkzeug.datastructures import FileStorage

#----Supabase
from supabase import create_client

#----Config
from config import Config

#----Grader
from grader import grader

app = Flask(__name__)
app.config.from_object(Config)

supabase = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

@app.route('/')
def home():
    """
    If user session exist. Sign user in with homepage, else direct to login page.

    Home route also checks and updates for first time users. If Users table cannot 
    find entries when searched with google_id, a new entry will be created using 
    the sessions google_id, name, and email.
    """
    user = session.get('user')
    if not user: return redirect(url_for("login"))
    return render_template('index.html', user=user)

@app.route('/login/')
def login():
    """
    Login page. If authenticated, redirect to home, else render login template
    """
    user = session.get('user')
    if user: return redirect(url_for("home"))
    return render_template('login.html')

@app.route('/login/auth/')
def login_auth():
    """
    Oauth intermediate route
    """
    callback_url = url_for('callback', _external=True) 
    response = supabase.auth.sign_in_with_oauth({"provider": 'google', 
    "options": {"redirect_to": callback_url}})
    return redirect(response.url)

@app.route('/callback/')
def callback():
    """
    Render template to immediately fetch tokens, redirect to store_token route which 
    redirect to home.

    This is a workaround to allow flask, a backend application to retrieve url fragments,
    which holds the authentication token returned from Google. 

    This page will not be shown to user, after login, client side will be rerouted 
    to final destination home. 
    """
    return render_template('callback.html')

@app.route('/store_token/', methods=['POST'])
def store_token():
    """
    Store authentication token and create/retrive User session data. 
    """
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
        
        check_user_in_database(session["user"]["id"], session["user"]["user_full_name"], session["user"]["user_email"])
        session["user"]["github_link"] = get_github_link_db(session["user"]["id"])
        checkpoint_submission = get_checkpoint_submission_db(session["user"]["user_email"])
        if checkpoint_submission["checkpoint0_filename"] is not None:
            session["user"]["checkpoint0_filename"] = checkpoint_submission["checkpoint0_filename"] 
            session["user"]["checkpoint0_last_submission_time"] = checkpoint_submission["checkpoint0_last_submission_time"] 
        if checkpoint_submission["checkpoint1_filename"] is not None:
            session["user"]["checkpoint1_filename"] = checkpoint_submission["checkpoint1_filename"] 
            session["user"]["checkpoint1_last_submission_time"] = checkpoint_submission["checkpoint1_last_submission_time"] 
        return redirect(url_for('home'))
    else:
        return "Error: Access token not found", 400

@app.route('/logout/')
def logout():
    """
    Clear session and log user out. 
    """
    session.clear()
    return redirect(url_for('login'))

@app.route('/submit_github_link/', methods=['POST'])
def submit_github_link():
    """
    Route for updating github link to database. Redirect to home for rerender. 
    """
    github_link = request.form.get('github_link')
    update_github_link_db(session["user"]["id"], github_link)
    session["user"]["github_link"] = github_link
    session.modified = True
    return redirect(url_for('home'))

@app.route('/upload_checkpoint_files/', methods=['POST'])
def upload_checkpoint_files():
    """
    Route for updating checkpoint files to database. Redirect to home for rerender
    """
    files = request.files.getlist('checkpoint_files')
    for file in files:
        if check_file_validity(file):
            new_filename = strip_uniquename_from_email(session["user"]["user_email"]) + "_" + file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename) 
            file.save(file_path)
            run_checkpoint_tests(file_path)
            response = upload_checkpoint_to_supabase(new_filename, file_path)
            if response.status_code == 200: 
                flash('Files uploaded successfully!', 'success')
                if file.filename == "checkpoint0.ipynb":
                    time = update_checkpoint_submission_db(session["user"]["user_email"], new_filename, 1)
                    session["user"]["checkpoint0_filename"] = new_filename
                    session["user"]["checkpoint0_last_submission_time"] = time 
                elif file.filename == "checkpoint1.ipynb":
                    time = update_checkpoint_submission_db(session["user"]["user_email"], new_filename, 0)
                    session["user"]["checkpoint1_filename"] = new_filename
                    session["user"]["checkpoint1_last_submission_time"] = time
                session.modified = True
            else:
                flash('File upload failed when sending to database', 'error')
            os.remove(file_path)
        else: 
            print("File not valid: Exceed size 500 KB or is not named checkpoint0.ipynb or checkpoint0.ipynb ")
            flash('File upload failed!', 'error')
    return redirect(url_for('home'))

######################################################
# Helper functions
######################################################
def check_user_in_database(uid: str, full_name: str, email) -> str:
    """
    Check if user is in database. If not add user to database in Users table with 
    google_id and create entry in the tutorial submission table with null values. 
    """
    response = supabase.from_('Users').select('google_id').eq('google_id', uid).execute()
    
    if not response.data:
        
        # Make an empty entry in tutorial submission table:
        # This empty entry would simplify our job when updating scores,
        # as we do note need to check for existance of an entry to update in tutorial
        # submission, it is all taken care of during user first time log in. 
        supabase.from_('Tutorial_Submission').insert({
            'email': email
        }).execute()
        print("Submission entry created in table: Submission")

        # Make an entry in users table
        supabase.from_('Users').insert({
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
    supabase.from_('Users').update({'github_link': github_link}).eq('google_id', uid).execute()


def get_github_link_db(uid:str) -> str:
    """
    Get github link for te user on Users table

        @params
            uid: google_id
    """
    response = supabase.from_('Users').select('github_link').eq('google_id', uid).execute()
    if response.data:
        return response.data[0]['github_link']

def run_checkpoint_tests(filepath: str):
    """
    Run checkpoint completion, compilation, correctness (if applicable) tests on the file

    Note this function expects a valid input and does not do additial checkings 
    on the file type, size etc. 
    """
    grader_instance = grader(filepath, app.config["CHECKPOINT_QUESTION_TAG"])
    grader_instance.check_cells_have_code()
    grader_instance.print_results()
    grader_instance.print_grade()


def update_checkpoint_submission_db(email: str, checkpoint_file_name: str, isCheckpoint0: bool) -> str:
    time_stamp = datetime.now(pytz.timezone('US/Eastern')).isoformat()
    if isCheckpoint0:
        supabase.from_('Tutorial_Submission').update({'checkpoint0_filename': checkpoint_file_name,
        'checkpoint0_last_submission_time': time_stamp}).eq('email', email).execute()
    else:
        supabase.from_('Tutorial_Submission').update({'checkpoint1_filename': checkpoint_file_name, 
        'checkpoint1_last_submission_time': time_stamp}).eq('email', email).execute()
    return time_stamp

def get_checkpoint_submission_db(email: str) -> list[str]:
    """

    """
    response = supabase.from_(
        'Tutorial_Submission').select('checkpoint0_filename, checkpoint0_last_submission_time,checkpoint1_filename, checkpoint1_last_submission_time').eq('email', email).execute()
    if response.data:
        return response.data[0]

def check_file_validity (file: FileStorage) -> bool:
    """
    Checks if file passes both extension and 
    """
    if file.content_length > app.config['MAX_FILE_SIZE']:
        return False
    if not file.filename in app.config['ALLOWED_FILENAMES']:
        return False
    return True

def upload_checkpoint_to_supabase(filename: str, filepath: str) -> requests.Response: 
    """
    Upload a checkpoint file to supabase bucket: "checkpoints".

    If file name already exist in bucket, override. 

    Note this function expects a valid input and does not do additial checkings 
    on the file type, size etc. 
    """
    return supabase.storage.from_('checkpoints').upload(filename, filepath, {'upsert':'true'})

def strip_uniquename_from_email(email: str) -> bool:
    """
    Strips the unique name from an email address given an email.

    Ex: weilez@umich.edu -> weilez
    """
    return email.split('@')[0]


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
