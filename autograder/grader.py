from typing import List, Tuple, Optional
import nbformat

class grader:
     
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

    def check_cells_have_code(self) -> List[Tuple[nbformat.NotebookNode, bool]]:
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

    def get_final_grade_percentage(self) -> None: 
        if self.total_cells_checked == 0:
            return 0.0
        return round((self.cells_containing_code / self.total_cells_checked) * 100, 2)    

    def get_final_grade_raw(self) -> int:
        if self.total_cells_checked == 0:
            return 0.0
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

# Example usage
if __name__ == "__main__":
    notebook_path = 'checkpoint0.ipynb'
    question_start_with = "# Question"

    grader_instance = grader(notebook_path, question_start_with)
    grader_instance.check_cells_have_code()
    grader_instance.print_results()
    grader_instance.print_grade()