import requests
import json

schema = {
    "database": "SchoolDB",
    "tables": [
        {
            "name": "Students",
            "columns": [
                {"name": "id", "datatype": "int", "is_pk": True},
                {"name": "name", "datatype": "text"},
                {"name": "age", "datatype": "int"}
            ]
        },
        {
            "name": "Courses",
            "columns": [
                {"name": "cid", "datatype": "int", "is_pk": True},
                {"name": "title", "datatype": "text"},
                {"name": "credits", "datatype": "int"}
            ]
        }
    ]
}

try:
    response = requests.post("http://localhost:8000/api/schema/update", json=schema)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Verify schema update by fetching it back
    print("\nFetching updated schema...")
    response = requests.get("http://localhost:8000/api/schema")
    print(f"Current Schema: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error: {e}")
