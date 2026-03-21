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


assignments_due = canvas_student.getAssignmentInfo("55069")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", 
         "content": 
         f"analyze my following assignments and make a brief summary of them:{assignments_due}"}
    ], stream=True
)

#Speed of groqs output
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        for letter in content:
            print(letter, end="", flush=True)
            time.sleep(0.01)

print() 
        