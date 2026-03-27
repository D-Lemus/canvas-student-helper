import requests
import json
from datetime import datetime, timezone
import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv
import time
import canvas_student

# PARA DESPUES:
    #function prompt { "Master ~ " } 

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_TOKEN"))


def startChatBot():
    assignments_due = canvas_student.getAllWeekAssignments()

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


            