import nbformat
from pathlib import Path
from config import Config, Mode
from typing import List, Dict, Optional


class Grader:
     
    def __init__(self, notebook_file_path: str, question_start_with: str, mode: Mode):
        """
        Constructor method to initialize instance attributes.

        Parameters:
        notebook_file_path: The file path of the Jupyter notebook.
        question_start_with: The string that the question cells start with.
        """
        self.notebook_file_path = notebook_file_path
        self.question_start_with = question_start_with
        self.notebook: Optional[nbformat.NotebookNode] = None
        self.mode = mode

        self.__load_notebook()
        self.cells_to_check: List[int] = self.__find_cells_to_check()

        self.cells_containing_code: int = 0
        self.total_cells_checked: int = 0
        self.final_score: int  = 0
        self.answers = []



    def __load_notebook(self) -> None:
        """
        Load the notebook from the specified file path.
        """
        with open(self.notebook_file_path, 'r', encoding='utf-8') as f:
            self.notebook = nbformat.read(f, as_version=4)

    def __find_cells_to_check(self) -> List[int]:
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


    def __check_cells_have_code(self):
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
            code_lines = [line for line in lines if not line.strip().startswith('#') and not line.strip() == '']
            has_code = any(code_lines)
            if has_code:
                self.cells_containing_code += 1
            results.append((cell, code_lines))
        self.answers = results
    
    def __grade_with_ai(self):
        """
        Grade the checkpoint using AI.
        """
        pass

    def get_final_grade_percentage(self) -> float: 
        if self.total_cells_checked == 0:
            return 0.0
        return round((self.final_score / self.total_cells_checked) * 100, 2)    

    def get_final_grade_raw(self) -> int:
        if self.total_cells_checked == 0:
            return 0 
        return self.final_score

    def grade_checkpoint(self) -> None:
        """
        Grade the checkpoint based on the number of cells containing code.
        """
        print(f"Grading in {self.mode} mode.")
        self.__check_cells_have_code()

        if self.mode == Mode.COMPLETION:
            pass
        elif self.mode == Mode.RUNNABLE:
            pass
        elif self.mode == Mode.CORRECTNESS:
            self.final_score = self.__grade_with_ai()

    def print_question_and_answer(self) -> None:
        """
        Print the results of checking if cells contain code. 
        This function is primarily used for debugging. 
        """
        if self.cells_containing_code == 0:
            print("No cells contain code.")
            return
        
        for cell, has_code in self.answers:
            first_line = cell.source.splitlines()[0] if cell.source.splitlines() else ""
            print(f"Cell with comment '{first_line}' has code: {has_code}")
    
    def get_question_and_answer(self) -> List[Dict[str, str]]:
        """
        Return the results of checking if cells contain code. 
        """
        return [{"question": question.source.splitlines()[0], "answer": answer} for question, answer in self.answers]
    
    def process_result(self, result: List[str])-> None:
        """
        Process the result of the grading.

        A sample: "["Question 1: Correct", "Question 2: No Answer Provided", "Question 3: Correct", "Question 4: No Answer Provided", "Question 5: No Answer Provided", "Question 6: No Answer Provided", "Question 7: Incorrect", "Question 8: No Answer Provided", "Question 9: No Answer Provided", "Question 10: No Answer Provided", "Question 11: No Answer Provided", "Question 12: No Answer Provided", "Question 13: No Answer Provided", "Question 14: No Answer Provided"]["Question 1: Correct", "Question 2: No Answer Provided", "Question 3: Correct", "Question 4: No Answer Provided", "Question 5: No Answer Provided", "Question 6: No Answer Provided", "Question 7: Incorrect", "Question 8: No Answer Provided", "Question 9: No Answer Provided", "Question 10: No Answer Provided", "Question 11: No Answer Provided", "Question 12: No Answer Provided", "Question 13: No Answer Provided", "Question 14: No Answer Provided"]"
        """
        result_list = [item.strip() for item in result.split(',')]
        for r in result_list:
            if "Correct" in r or "Almost Correct" in r:
                self.final_score += 1
    
    def print_grade(self) -> None:
        """
        Print the grade base on the number of cells containing code divided by the total cells checked.
        This function is primarily used for debugging. 
        """
        if self.total_cells_checked == 0:
            print("No cells checked.")
            return
        print("\nPrinting completion grade ------------------")
        grade = (self.final_score / self.total_cells_checked) * 100
        print(f"\nTotal cells checked (Questions): {self.total_cells_checked}")
        print(f"Cells Correct (Answers): {self.final_score}")
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
    
    grader_instance = Grader(filepath, Config.CHECKPOINT_QUESTION_TAG, Config.GRADER_MODE)
    grader_instance.grade_checkpoint()
    grader_instance.print_question_and_answer()
    grader_instance.print_grade()
    
    return {"raw_score": grader_instance.get_final_grade_raw(), 
            "percent_score": grader_instance.get_final_grade_percentage()}
