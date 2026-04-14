import requests
import json
from datetime import datetime, timezone
import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

CANVAS_URL = os.getenv("CANVAS_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_TOKEN"))

def obtain_courses():
    courses = []
    response = requests.get(
        f"{CANVAS_URL}api/v1/courses",
        headers={"Authorization": f"Bearer {CANVAS_API_TOKEN}"},
        params={"enrollment_type":"student", "per_page": 100, "enrollment_term_id": 326},
    )

    #print(json.dumps(response.json(), indent=2))

    for course in response.json():
        if "name" not in course:
            continue
        if "P2026" in course["name"]:
            courses.append(int(course["id"]))

    return courses



def _get_assignments_from_a_course(course_id : str):
    response = requests.get(
        f"{CANVAS_URL}api/v1/courses/{course_id}/assignments",
        headers={"Authorization": f"Bearer {CANVAS_API_TOKEN}"},
        params={"order_by":"due_at", "per_page": 100},
    )

    return response.json()

def get_due_assignments(course_id : str):
    
    assignments = _get_assignments_from_a_course(course_id)
    now = datetime.now(timezone.utc)
    week_from_now = now + pd.Timedelta(days=7)
    due_assignments = []

    for assignment in assignments:
        due_at_str = assignment["due_at"]
        if not due_at_str:
            continue
        due_at= datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
        if (not assignment.get("has_submitted_submissions", False) and 
                due_at >= now and                    # not overdue
                due_at <= week_from_now):            # within next 7 days
                due_assignments.append(assignment)

    return due_assignments

def _get_assignments_info(course_id : str):
    assignments_due= get_due_assignments(course_id)

    name_and_description = {}

    for assignment in assignments_due:
        name = assignment["name"]
        description = assignment.get("description")

        name_and_description[name]= description
                
    return name_and_description


def get_all_week_assignments():
    courses = obtain_courses()
    assignments = []

    for course in courses:
        assignments.append(_get_assignments_info(course))

    print(list(assignments))
    print(json.dumps(assignments, indent=2))
    return assignments
    
a = get_all_week_assignments()



