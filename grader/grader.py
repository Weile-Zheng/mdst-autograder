import nbformat
from pathlib import Path
from config import Config
from typing import List, Dict, Optional

class Grader:
     
    def __init__(self, notebook_file_path: str, question_start_with: str):
        """
        Constructor method to initialize instance attributes.

        Parameters:
        notebook_file_path: The file path of the Jupyter notebook.
        question_start_with: The string that the question cells start with.
        """
        self.notebook_file_path = notebook_file_path
        self.question_start_with = question_start_with
        self.notebook: Optional[nbformat.NotebookNode] = None

        self.load_notebook()
        self.cells_to_check: List[int] = self.find_cells_to_check()

        self.cells_containing_code: int = 0
        self.total_cells_checked: int = 0
        self.final_score: int  = 0
        self.result = []


    def load_notebook(self) -> None:
        """
        Load the notebook from the specified file path.
        """
        with open(self.notebook_file_path, 'r', encoding='utf-8') as f:
            self.notebook = nbformat.read(f, as_version=4)

    def find_cells_to_check(self) -> List[int]:
        """
        Find all cell indices that start with the specified string and return them as a list.

        Returns:
            A list of indices of cells that start with the specified string.
        """
        if self.notebook is None:
            raise ValueError("Notebook not loaded. Call load_notebook() first.")
        
        return [
            idx for idx, cell in enumerate(self.notebook.cells)
            if cell.cell_type == 'code' and cell.source.strip().startswith(self.question_start_with)
        ]

    def check_cells_have_code(self):
        """
        Check if cells with comments starting with 'Question' contain code.

        Returns:
            A list of tuples containing the cell and whether it has code.
        """
        if self.notebook is None:
            raise ValueError("Notebook not loaded. Call load_notebook() first.")
        
        results = []
        self.total_cells_checked = len(self.cells_to_check)
        self.cells_containing_code = 0
        for idx in self.cells_to_check:
            cell = self.notebook.cells[idx]
            lines = cell.source.split('\n')
            code_lines = [line for line in lines if not line.strip().startswith('#')]
            has_code = any(code_lines)
            if has_code:
                self.cells_containing_code += 1
            results.append((cell, has_code))
        self.result = results

    def get_final_grade_percentage(self) -> float: 
        if self.total_cells_checked == 0:
            return 0.0
        return round((self.cells_containing_code / self.total_cells_checked) * 100, 2)    

    def get_final_grade_raw(self) -> int:
        if self.total_cells_checked == 0:
            return 0 
        return self.cells_containing_code

    def print_results(self) -> None:
        """
        Print the results of checking if cells contain code. 
        This function is primarily used for debugging. 
        """
        if self.total_cells_checked == 0:
            print("No cells checked.")
            return
        for cell, has_code in self.result:
            first_line = cell.source.splitlines()[0] if cell.source.splitlines() else ""
            print(f"Cell with comment '{first_line}' has code: {has_code}")
    
    def print_grade(self) -> None:
        """
        Print the grade base on the number of cells containing code divided by the total cells checked.
        This function is primarily used for debugging. 
        """
        if self.total_cells_checked == 0:
            print("No cells checked.")
            return
        print("\nPrinting completion grade ------------------")
        grade = (self.cells_containing_code / self.total_cells_checked) * 100
        print(f"\nTotal cells checked (Questions): {self.total_cells_checked}")
        print(f"Cells containing code (Answers): {self.cells_containing_code}")
        print(f"Grade: {grade:.2f}%")


def run_checkpoint_tests(filepath: str) -> Dict[str, int | float]:
    """
    Run checkpoint completion, compilation, correctness (if applicable) tests on the file

    Note this function expects a valid input and does not do additional checks
    on the file type, size etc. 

    Returns a dict on computed "raw_score" and "percent_score"
    {
        "raw_score": int,
        "percent_score": float
    }
    """
    path = Path(filepath).resolve()
    print(f"Running grade tests on file: {path}")
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist.")
    
    grader_instance = Grader(filepath, Config.CHECKPOINT_QUESTION_TAG)
    grader_instance.check_cells_have_code()
    grader_instance.print_results()
    grader_instance.print_grade()
    
    return {"raw_score": grader_instance.get_final_grade_raw(), 
            "percent_score": grader_instance.get_final_grade_percentage()}


from util import download_checkpoint, Message
from db import upload_score
import os
import json
if __name__ == "__main__":
    msg = {"email": "weilez@umich.edu", "checkpoint": 0, "url": "https://ztabaafahvxlvhoejunj.supabase.co/storage/v1/object/sign/checkpoints/weilez_checkpoint0.ipynb?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGVja3BvaW50cy93ZWlsZXpfY2hlY2twb2ludDAuaXB5bmIiLCJpYXQiOjE3MzgyOTYxMjMsImV4cCI6MTc0MzQ4MDEyM30.jCMUdPOj1ekkfrmY9bkOSL99h7T8Tiw_ClRSHKMXMXk&download=weilez_checkpoint0.ipynb"}
    
    msg_obj = Message.from_json(json.dumps(msg))
    email, checkpoint, url = msg_obj.email, msg_obj.checkpoint, msg_obj.url
    temp_file = f"checkpoint{checkpoint}.ipynb"

    print("Downloading checkpoint file from URL.")
    download_checkpoint(url, name=temp_file)

    print("Running checkpoint tests.")
    result = run_checkpoint_tests(temp_file)

    print("Uploading score to database.")
    success = upload_score(email, checkpoint, result["raw_score"], result["percent_score"])

    if success:
        print("Score uploaded successfully, cleaning up.")
        os.remove(temp_file)
    else: 
        print("Error uploading score to database.")
        raise Exception("Error uploading score to database.")

    