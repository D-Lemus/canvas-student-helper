import requests
import json
from datetime import datetime, timezone
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

CANVAS_URL = os.getenv("CANVAS_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")


def obtainCourses():
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

#course_id = "55069"
def getAssignmentsJson(course_id:str):
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
                print(json.dumps(assignment, indent=2))
                
                
a = getAssignmentsJson("55069")







