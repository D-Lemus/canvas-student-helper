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


def _getAssignmentsFromACourse(course_id : str):
    response = requests.get(
        f"{CANVAS_URL}api/v1/courses/{course_id}/assignments",
        headers={"Authorization": f"Bearer {CANVAS_API_TOKEN}"},
        params={"order_by":"due_at", "per_page": 100},
    )

    return response.json()

def _getDueAssignments(course_id : str):
    
    assignments = _getAssignmentsFromACourse(course_id)
    now = datetime.now(timezone.utc)
    due_assignments = []

    for assignment in assignments:
        due_date = assignment["due_at"]
        if due_date:
            due_at = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            if assignment["has_submitted_submissions"]==False and due_at > now:
                due_assignments.append(assignment)

    return due_assignments

def getAssignmentInfo(course_id : str):
    assignments_due= _getDueAssignments(course_id)

    name_and_description = {}

    for assignment in assignments_due:
        name = assignment["name"]
        description = assignment.get("description")

        name_and_description[name]= description
                
    return name_and_description




