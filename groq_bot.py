import os
from groq import Groq
from dotenv import load_dotenv
import canvas_student

# PARA DESPUES:
    #function prompt { "Master ~ " } 

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_TOKEN"))


def start_chat_bot():
    assignments_due = canvas_student.get_all_week_assignments()

    result = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", 
            "content": 
            f"""analyze my following assignments and do me an assignment 
            backlog based on a proprity stategy take into account 
            the following assignments:
            {assignments_due}"""}
        ],
    )

    return result

#startChatBot("55069")


#Speed of groqs output


            