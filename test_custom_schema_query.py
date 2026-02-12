import requests
import json
import time

base_url = "http://localhost:8000"

def run_test():
    # 1. Upload Schema
    print("Uploading Schema...")
    with open("student_advisor_schema.json", "r") as f:
        schema_data = json.load(f)
    
    try:
        response = requests.post(f"{base_url}/api/schema/update", json=schema_data)
        if response.status_code == 200:
            print("Schema uploaded successfully.")
        else:
            print(f"Failed to upload schema: {response.text}")
            return
    except Exception as e:
        print(f"Error uploading schema: {e}")
        return

    output = []
    query = "List the names of students and their advisors in the Computer Science department who have a GPA above 3.5"
    output.append(f"\nQuery: {query}")
    
    try:
        response = requests.post(f"{base_url}/api/translate", json={"query": query})
        if response.status_code == 200:
            data = response.json()
            output.append(f"SQL: {data['sql']}")
            output.append(f"Structure: {json.dumps(data['query_structure'], indent=2)}")
        else:
            output.append(f"Error executing query: {response.text}")
    except Exception as e:
        output.append(f"Error executing query: {e}")
        
    with open("custom_test_results.log", "w") as f:
        f.write("\n".join(output))
    print("\n".join(output))

if __name__ == "__main__":
    run_test()
