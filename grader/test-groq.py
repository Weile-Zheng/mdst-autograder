import os
import json
from dotenv import load_dotenv
from groq import Groq
from grader import Grader
from config import Mode
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
                    
                    You must strictly follow the format I provided
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


def run_check():
    grader = Grader("weilez.ipynb", "# @@@", Mode.COMPLETION)
    grader.grade_checkpoint()
    answer = str(grader.get_question_and_answer())
    print(answer)
    print(type(answer))

    print("Checking answer with GROQ...")
    check_answer_with_groq(answer)

if __name__ == "__main__":
    run_check()
