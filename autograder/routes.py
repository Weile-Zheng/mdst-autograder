#----Utils----
import os
from autograder.util import *
from autograder.db import *

#----Flask----
from autograder import supabase_client
from flask import redirect, url_for, request, session, render_template, flash

@autograder.app.route('/')
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

@autograder.app.route('/login/')
def login():
    """
    Login page. If authenticated, redirect to home, else render login template
    """
    user = session.get('user')
    if user: return redirect(url_for("home"))
    return render_template('login.html')

@autograder.app.route('/login/auth/')
def login_auth():
    """
    Oauth intermediate route
    """
    callback_url = url_for('callback', _external=True) 
    response = supabase_client.auth.sign_in_with_oauth({"provider": 'google', 
    "options": {"redirect_to": callback_url}})
    return redirect(response.url)

@autograder.app.route('/callback/')
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

@autograder.app.route('/store_token/', methods=['POST'])
def store_token():
    """
    Store authentication token and create/retrive User session data. 
    """
    access_token = request.form.get('access_token')


    if access_token:
        session['access_token'] = access_token
        user_info = supabase_client.auth.get_user(access_token).user
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
        uniquename = uniquename_from_email(session["user"]["user_email"])
        if checkpoint_submission["checkpoint0_filename"] is not None:
            session["user"]["checkpoint0_filename"] = checkpoint_submission["checkpoint0_filename"] 
            session["user"]["checkpoint0_last_submission_time"] = checkpoint_submission["checkpoint0_last_submission_time"] 
            session["user"]["checkpoint0_url"] = get_checkpoint_file_url(f"{uniquename}_checkpoint0.ipynb", "checkpoints")
        if checkpoint_submission["checkpoint1_filename"] is not None:
            session["user"]["checkpoint1_filename"] = checkpoint_submission["checkpoint1_filename"] 
            session["user"]["checkpoint1_last_submission_time"] = checkpoint_submission["checkpoint1_last_submission_time"] 
            session["user"]["checkpoint1_url"] = get_checkpoint_file_url(f"{uniquename}_checkpoint1.ipynb", "checkpoints")
            print(f"checkpoint1: url {session["user"]["checkpoint1_url"]}")
        return redirect(url_for('home'))
    else:
        return "Error: Access token not found", 400

@autograder.app.route('/logout/')
def logout():
    """
    Clear session and log user out. 
    """
    session.clear()
    return redirect(url_for('login'))

@autograder.app.route('/submit_github_link/', methods=['POST'])
def submit_github_link():
    """
    Route for updating github link to database. Redirect to home for rerender. 
    """
    github_link = request.form.get('github_link')
    update_github_link_db(session["user"]["id"], github_link)
    session["user"]["github_link"] = github_link
    session.modified = True
    return redirect(url_for('home'))

@autograder.app.route('/upload_checkpoint_files/', methods=['POST'])
def upload_checkpoint_files():
    """
    Route for updating checkpoint files to database. Redirect to home for rerender
    """
    files = request.files.getlist('checkpoint_files')
    upload_directory = autograder.app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    for file in files:
        if check_file_validity(file, autograder.app.config["MAX_FILE_SIZE"], autograder.app.config["ALLOWED_FILENAMES"]):
            new_filename = uniquename_from_email(session["user"]["user_email"]) + "_" + file.filename
            file_path = os.path.join(upload_directory, new_filename) 
            file.save(file_path)
            score = run_checkpoint_tests(file_path)
            response = upload_checkpoint_to_supabase(new_filename, file_path)
            if response.status_code == 200: 
                flash('Files uploaded successfully!', 'success')

                if file.filename == "checkpoint0.ipynb":
                    time = update_checkpoint_submission_db(
                        session["user"]["user_email"], 
                        new_filename, 
                        1,
                        score["raw_score"],
                        score["percent_score"])
                    
                    session["user"]["checkpoint0_filename"] = new_filename
                    session["user"]["checkpoint0_last_submission_time"] = time 
                    session["user"]["checkpoint0_url"] = get_checkpoint_file_url(new_filename, "checkpoints")

                elif file.filename == "checkpoint1.ipynb":
                    time = update_checkpoint_submission_db(
                            session["user"]["user_email"], 
                            new_filename, 
                            0,
                            score["raw_score"],
                            score["percent_score"])
                    
                    session["user"]["checkpoint1_filename"] = new_filename
                    session["user"]["checkpoint1_last_submission_time"] = time
                    session["user"]["checkpoint1_url"] = get_checkpoint_file_url(new_filename, "checkpoints")

                session.modified = True
            else:
                flash('File upload failed when sending to database', 'error')
            os.remove(file_path)
        else: 
            print("File not valid: Exceed size 500 KB or is not named checkpoint0.ipynb or checkpoint0.ipynb ")
            flash('File upload failed!', 'error')
    return redirect(url_for('home'))