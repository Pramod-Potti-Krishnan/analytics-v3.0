#!/usr/bin/env python3
import requests
import json

response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "test",
        "slide_id": "test-1",
        "slide_number": 1,
        "narrative": "Test revenue over time",
        "data": [
            {"label": "Q1", "value": 100},
            {"label": "Q2", "value": 150}
        ]
    }
)

print("Status Code:", response.status_code)
print("\nResponse JSON:")
print(json.dumps(response.json(), indent=2))
