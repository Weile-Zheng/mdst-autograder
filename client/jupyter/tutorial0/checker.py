import nbformat

def check_question_cells_have_code(notebook_path: str, cell_start_with: str):
    """
    Check if the presented notebook have code in them. Ignoring all comments

    @params
        notebook_path: path to the notebook file.
        cell_start_with: only cells that start with this string will be checked. 
    """
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Iterate through the cells and check if they contain code
    question_cells = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            in_question_block = False
            code_lines = []
            for line in lines:
                if line.strip().startswith(cell_start_with):
                    in_question_block = True
                if in_question_block and not line.strip().startswith('#'):
                    code_lines.append(line)
            
            if in_question_block:
                has_code = any(code_lines)
                question_cells.append((cell, has_code))
    
    return question_cells

def check_cells_for_errors(notebook_path):
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Iterate through the cells and check for errors
    cell_errors = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            code = cell.source
            try:
                exec(code, {})
                cell_errors.append((cell, False, None))
            except Exception as e:
                cell_errors.append((cell, True, str(e)))
    
    return cell_errors

# Example usage
notebook_path = "checkpoint0.ipynb"
cell_start = "# Question"

# Check if cells with comments starting with "Question" contain code
question_result = check_question_cells_have_code(notebook_path, cell_start_with=cell_start)
for cell, has_code in question_result:
    first_line = cell.source.splitlines()[0] if cell.source.splitlines() else ""
    print(f"Cell with comment '{first_line}' has code: {has_code}")

#---------------------------------------------------------------------------------------


# Check if cells have errors
error_result = check_cells_for_errors(notebook_path)
for cell, has_error, error_message in error_result:
    first_line = cell.source.splitlines()[0] if cell.source.splitlines() else continue
    if has_error:
        print(f"Cell with code '{first_line}' has error: {error_message}")
    else:
        print(f"Cell with code '{first_line}' has no errors")