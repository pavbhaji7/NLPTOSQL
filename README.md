# G-SQL: Rule-Guided Natural Language to SQL Translation

## Overview
G-SQL is a robust, schema-aware system that translates Natural Language Queries (NLQ) into SQL queries. Unlike opaque "black-box" LLM approaches, G-SQL uses a transparent, rule-guided pipeline involving **Semantic Tagging**, **Schema Linking**, and **Logic Inference**.

This project implements the core G-SQL logic in Python and provides a modern, interactive web interface to visualize exactly how your question becomes specific SQL code.

## How It Works (The "Improvisation")
The system follows a transparent pipeline, visible in the UI:
1.  **NLP & Tagging**: The system breaks down your sentence and identifies:
    *   **Meta**: Table or Column names (e.g., "Movie", "budget").
    *   **Value**: Specific data values (e.g., "Avatar", "2000").
    *   **Logic**: Aggregations (SUM, AVG) or Conditions (>, <).
2.  **Schema Linking**: It maps these tags to the specific database schema (IMDB-like sample provided).
3.  **Graph-Based Join Inference**: If you ask for specific data across tables (e.g., "Actors in Avatar"), it creates the necessary SQL JOINs automatically by finding paths in the schema graph.
4.  **Generation**: Constructs the valid SQL query.

## Project Structure
*   `gsql/`: Core Python library implementation (NLP, Tagger, Linker, Generator).
*   `server.py`: FastAPI backend that exposes the G-SQL logic.
*   `frontend/`: React + Vite application for the user interface.

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   Node.js & npm

### 1. Backend Setup
1.  Navigate to the project root:
    ```bash
    cd c:\Users\gsjit\minor\nlptosql
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the API server:
    ```bash
    python server.py
    ```
    *The server will start on `http://localhost:8000`*

### 2. Frontend Setup
1.  Open a new terminal and navigate to the frontend directory:
    ```bash
    cd c:\Users\gsjit\minor\nlptosql\frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *The UI will run on `http://localhost:5173`*

## Usage
1.  Open `http://localhost:5173` in your browser.
2.  You will see the **Database Schema** on the left (Movies, Actors, Directors).
3.  Type a query in the input box, for example:
    *   *"Show me movies released after 2000"*
    *   *"List actors who played in Avatar"*
    *   *"Find directors of films with budget greater than 1000000"*
4.  Click **Translate**.
5.  Observe the **Pipeline Visualization** chips to understand how G-SQL parsed your request.
6.  Copy the generated SQL from the result block.

## Example Queries
Here are some example queries you can try, which the G-SQL schema supports:

### Basic Select
*   "Show movies"
*   "List actors"
*   "Find all directors"

### Filtering (Conditions)
*   "Movies released after 2000"
*   "Films with budget greater than 1000000"
*   "Actors where gender is Male"

### Joins (Cross-Table)
*   "Actors in Avatar"
*   "Director of Titanic"
*   "Role of Brad Pitt in Fight Club"
*   "Movies directed by Nolan"
