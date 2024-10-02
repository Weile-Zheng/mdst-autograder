
import autograder
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

def uniquename_from_email(email: str) -> bool:
    """
    Strips the unique name from an email address given an email.

    Ex: weilez@umich.edu -> weilez
    """
    return email.split('@')[0]

def run_checkpoint_tests(filepath: str) -> Dict[str, int]:
    """
    Run checkpoint completion, compilation, correctness (if applicable) tests on the file

    Note this function expects a valid input and does not do additial checkings 
    on the file type, size etc. 

    Returns a dict on computed "raw_score" and "percent_score"
    """
    grader_instance = grader(filepath, autograder.app.config["CHECKPOINT_QUESTION_TAG"])
    grader_instance.check_cells_have_code()
    grader_instance.print_results()
    grader_instance.print_grade()
    return {"raw_score": grader_instance.get_final_grade_raw(), 
            "percent_score": grader_instance.get_final_grade_percentage()}