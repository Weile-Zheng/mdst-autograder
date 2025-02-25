import os
from dotenv import load_dotenv
from groq import Groq
from grader import Grader
from config import Mode
from config import Config
load_dotenv()

def check_answer_with_groq(question_answer) -> None:
    """
    Check the answer with GROQ.
    """
    
    client = Groq(
        # This is the default and can be omitted
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": 
                """ You are an expert in Python and data science. You will help me grade
                    questions from a student. He is using Python and the Pandas Library. Provided
                    with a list of Dict, where each Dict have the attribute question and answer, you 
                    will help me grade the student's answers. Your returned output should be a list
                    from Question 1 to Question N, following by an answer of either Correct, Almost Correct, Incorrect, and No Answer Provided.

                    Example Input: [{"question": "# @@@ Question 1: here is a Python list:", "answer": ["a = [1, 2, 3, 4, 5, 6]"]}, {"question": "# @@@ Question 2: get a list containing the last 3 elements of a", "answer": []}

                    Example Output: ["Question 1: Correct", "Question 2: No Answer Provided"]
                    
                    You must strictly follow the format I provided. DO NOT give any more additional lines, blank or nonblank.
                """
            },
            {
                "role": "user",
                "content": "This is the question and answer list, start grading: /n" + question_answer ,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


def run_check(notebook_path: str, question_tag: str, mode: Mode) -> None:
    grader = Grader(notebook_path, question_tag, mode)
    grader.check_cells_have_code()
    answer = str(grader.get_question_and_answer())
    print(answer)
    print("Checking answer with GROQ...")
    result = check_answer_with_groq(answer)

    grader.process_result(result)
    return grader.get_final_grade_raw(), grader.get_final_grade_percentage()

if __name__ == "__main__":
    raw_score, percent_score = run_check("weilez.ipynb", Config.CHECKPOINT_QUESTION_TAG , Mode.CORRECTNESS)
    print(raw_score, percent_score)
