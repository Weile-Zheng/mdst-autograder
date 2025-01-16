
import autograder
import pytz
from datetime import datetime
from typing import Dict
from autograder.grader import grader
from werkzeug.datastructures import FileStorage

def check_file_validity (file: FileStorage, maxFileSize: int, allowedFileNames: set) -> bool:
    """
    Checks if file passes both extension and max file size test. 
    """
    if file.content_length > maxFileSize:
        return False
    if not file.filename in allowedFileNames:
        return False
    return True

def to_est(iso_timestamp: str) -> str:
    """
    Converts a given ISO timestamp to Eastern Standard Time (EST).
    """
    utc_time = datetime.fromisoformat(iso_timestamp)
    est_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
    human_readable_time = est_time.strftime('%Y-%m-%d %H:%M:%S')
    return human_readable_time

def uniquename_from_email(email: str) -> str:
    """
    Strips the unique name from an email address given an email.

    Ex: weilez@umich.edu -> weilez
    """
    return email.split('@')[0]

def run_checkpoint_tests(filepath: str) -> Dict[str, int]:
    """
    Run checkpoint completion, compilation, correctness (if applicable) tests on the file

    Note this function expects a valid input and does not do additional checks
    on the file type, size etc. 

    Returns a dict on computed "raw_score" and "percent_score"
    """
    grader_instance = grader(filepath, autograder.app.config["CHECKPOINT_QUESTION_TAG"])
    grader_instance.check_cells_have_code()
    grader_instance.print_results()
    grader_instance.print_grade()
    return {"raw_score": grader_instance.get_final_grade_raw(), 
            "percent_score": grader_instance.get_final_grade_percentage()}