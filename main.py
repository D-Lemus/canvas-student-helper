import requests
import json
from datetime import datetime, timezone
import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv
import time

load_dotenv()

CANVAS_URL = os.getenv("CANVAS_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_TOKEN"))

response = requests.get(
    f"{CANVAS_URL}api/v1/courses",
    headers={"Authorization": f"Bearer {CANVAS_API_TOKEN}"},
    params={"enrollment_type":"student", "per_page": 100, "enrollment_term_id": 326},
)

#print(json.dumps(response.json(), indent=2))

for course in response.json():
    if "name" not in course:
        continue
    if "P2026" not in course["name"]:
        continue
    #print(course["id"], course["name"])


# ASSIGNMENTS
print("="*30)
course_id = "55069"
response2 = requests.get(
    f"{CANVAS_URL}api/v1/courses/{course_id}/assignments",
    headers={"Authorization": f"Bearer {CANVAS_API_TOKEN}"},
    params={"order_by":"due_at", "per_page": 100},
)

#print(json.dumps(response2.json(), indent=2))

now = datetime.now(timezone.utc)

assignments_due = []
for assignment in response2.json():
    if assignment["due_at"]:

        due_at_str = assignment["due_at"] 
        due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))

        if assignment["has_submitted_submissions"]==False and due_at > now:
            #print(assignment["name"])
            assignments_due.append(assignment["name"])


response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": f"analyze my following assignments and make a brief summary of them:{assignments_due}"}
    ], stream=True
)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
        time.sleep(0.1)

print()  # new line when done
        

