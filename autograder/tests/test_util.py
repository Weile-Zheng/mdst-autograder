from autograder.util import * 
from werkzeug.datastructures import FileStorage
from io import BytesIO


MAX_FILE_SIZE = 500 * 1024  # Multiply by 1024 for KB
ALLOWED_FILENAMES = {"checkpoint0.ipynb", "checkpoint1.ipynb"}

def test_check_file_validity():
    # File size and name valid -> valid
    file = FileStorage(stream=BytesIO(b"dummy content"), filename="checkpoint0.ipynb", content_length=100*1024)
    assert check_file_validity(file, MAX_FILE_SIZE, allowedFileNames=ALLOWED_FILENAMES) == True

    # File size not valid but name valid -> invalid
    file = FileStorage(stream=BytesIO(b"dummy content"), filename="checkpoint0.ipynb", content_length=600*1024)
    assert check_file_validity(file, MAX_FILE_SIZE, allowedFileNames=ALLOWED_FILENAMES) == False

    # File size valid but name invalid -> invalid
    file = FileStorage(stream=BytesIO(b"dummy content"), filename="checkpoint0.txt", content_length=100*1024)
    assert check_file_validity(file, MAX_FILE_SIZE, allowedFileNames=ALLOWED_FILENAMES) == False

    # File size invalid and name invalid -> invalid
    file = FileStorage(stream=BytesIO(b"dummy content"), filename="checkpoint0.txt", content_length=1000*1024)
    assert check_file_validity(file, MAX_FILE_SIZE, allowedFileNames=ALLOWED_FILENAMES) == False 

def test_uniquename_from_email():
    assert uniquename_from_email("weilez@umich.edu") == "weilez"
    assert uniquename_from_email("bigpanda@example.com") == "bigpanda"
    assert uniquename_from_email("amiralid@domain.com") == "amiralid"

def test_grader_correctness():
    # Test the correctness of autograder. 
    pass