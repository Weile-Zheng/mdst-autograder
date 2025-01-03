import pytest
import random
import time

from autograder import app
from autograder.db import *

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

mock_user = {
            'id': 'b59773aa-3f9c-4ffc-9f5d-8069ab1a7d88', # Non sensitive mock ID 
            'user_full_name': 'testuser',
            'user_email': 'testuser@gmail.com',
            'user_picture': 'http://example.com/picture.jpg'
            }

def test_login_page(client):
    response = client.get('/login/')
    assert response.status_code == 200

def test_homepage_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302 # Redirect 
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200 #  Login page

def test_homepage_logged_in(client):
    with client.session_transaction() as session:
        session["user"] = mock_user

    response = client.get('/')
    assert response.status_code == 200 # Direct access to homepage

def polling_update(async_func: callable, data: dict, check_value: str, max_attempts = 5, sleep_time = 1) -> bool:
    """
    Polling function to check the status of async function. 
    """
    for _ in range(max_attempts):
        if async_func(data) == check_value:
            print(f"Value {check_value} found in database")
            return True
        time.sleep(sleep_time)
    return False
    

def test_upload_github_link(client):
    with client.session_transaction() as session:
        session["user"] = mock_user

    rand = random.randint(1000,9999)
    link = f"https://github.com/testuser/repo/{rand}"

    response = client.post('/submit_github_link/', 
            data={'github_link': link})
    assert(response.status_code == 302) # Redirect
    assert polling_update(get_github_link_db, mock_user['id'], link) == True

def test_upload_valid_checkpoint_files(client):
    pass

def test_upload_invalid_checkpoint_files(client):
    pass

def test_upload_edgecase(client):
    pass

def load_test(client):
    pass

