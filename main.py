import requests
import json

CANVAS_URL = "https://canvas.iteso.mx/"
API_TOKEN = "12734~BYDFyTM2xLAyRzQUFuzu7ePamVNfrMQeKCxR6RFMQeHUQtzHee3vZ7vxF62uZcBH"

response = requests.get(
    f"{CANVAS_URL}api/v1/courses",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    params={"enrollment_type":"student", "per_page": 10},
)

#print(json.dumps(response.json(), indent=2))

for course in response.json():
    if "name" not in course:
        continue
    print(course["id"],course["name"])


