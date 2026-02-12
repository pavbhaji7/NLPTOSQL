import requests
import json
import time

# Wait for server to start
time.sleep(2)

base_url = "http://localhost:8000/api/translate"


def test_query(query, description):
    output = []
    output.append(f"\n--- {description} ---")
    output.append(f"Query: {query}")
    try:
        response = requests.post(base_url, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            output.append(f"SQL: {data['sql']}")
            output.append(f"Structure: {json.dumps(data['query_structure'], indent=2)}")
        else:
            output.append(f"Error: {response.text}")
    except Exception as e:
        output.append(f"Exception: {str(e)}")
    
    with open("test_results.log", "a") as f:
        f.write("\n".join(output) + "\n")
    print("\n".join(output))

# Clear log file
open("test_results.log", "w").close()


# Ensure schema is loaded (it should be the default one on restart)
# Default schema: Movie, Actor, Cast, Director, Directed

# Test 1: Explicit Join / Multiple Tables
# "Show titles of movies and names of actors" -> Should join Movie and Actor (via Cast)
test_query("Show titles of movies and names of actors", "Implicit Join (Multi-table Select)")

# Test 2: Nested Query (AVG)
# "movies with budget higher than average budget"
test_query("movies with budget higher than average budget", "Nested Query (AVG)")

# Test 3: Nested Query (MAX)
# "movies with release_year after maximum release_year" (Silly query but tests logic)
test_query("movies with release_year after maximum release_year", "Nested Query (MAX)")

# Test 4: Explicit "Join" wording (relying on table detection)
# "Join Director and Movie"
test_query("names of directors and titles of movies", "Explicit Join via Nouns")
