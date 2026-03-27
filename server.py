from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import csv
import io
import sqlparse
import re

# Add current directory to path so we can import gsql modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gsql.schema import DatabaseSchema, Table, Column, JSONSerializer, DomainDictionary
from gsql.nlp import NLPProcessor
from gsql.tagger import SemanticTagger
from gsql.linker import SchemaLinker
from gsql.generator import SQLGenerator

app = FastAPI(title="G-SQL API", description="API for G-SQL Natural Language to SQL Translation")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize G-SQL components
# We'll use the sample schema from run.py for now
def create_sample_schema():
    # IMDB-like schema
    # Movie(mid, title, release_year, budget)
    # Actor(aid, name, gender)
    # Cast(aid, mid, role)
    # Director(did, name)
    # Directed(did, mid)
    
    movie = Table("Movie", [
        Column("mid", "int", is_pk=True),
        Column("title", "text"),
        Column("release_year", "int"),
        Column("budget", "float")
    ])
    
    actor = Table("Actor", [
        Column("aid", "int", is_pk=True),
        Column("name", "text"),
        Column("gender", "text")
    ])
    
    cast = Table("Cast", [
        Column("aid", "int", is_fk=True, fk_ref="Actor.aid"),
        Column("mid", "int", is_fk=True, fk_ref="Movie.mid"),
        Column("role", "text")
    ])

    director = Table("Director", [
        Column("did", "int", is_pk=True),
        Column("name", "text")
    ])

    directed = Table("Directed", [
        Column("did", "int", is_fk=True, fk_ref="Director.did"),
        Column("mid", "int", is_fk=True, fk_ref="Movie.mid")
    ])

    schema = DatabaseSchema("IMDB", [movie, actor, cast, director, directed])
    
    domain_dict = DomainDictionary()
    domain_dict.add_synonym("film", "table", "Movie")
    domain_dict.add_synonym("player", "table", "Actor")
    domain_dict.add_synonym("released", "column", "Movie.release_year")
    
    return schema, domain_dict

schema_history: Dict[str, DatabaseSchema] = {}
active_schema_name: str = "IMDB"

schema, domain_dict = create_sample_schema()
schema_history[active_schema_name] = schema

try:
    nlp = NLPProcessor()
except OSError:
    print("Spacy model not found. Downloading...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = NLPProcessor()

tagger = SemanticTagger(schema, domain_dict)
linker = SchemaLinker(schema)
generator = SQLGenerator()

def parse_sql_ddl(sql_text: str, default_name: str) -> DatabaseSchema:
    statements = sqlparse.split(sql_text)
    tables = []
    
    for stmt in statements:
        parsed = sqlparse.parse(stmt)
        if not parsed:
            continue
        stmt_parsed = parsed[0]
        
        stmt_str = str(stmt_parsed).strip()
        if re.search(r'CREATE\s+TABLE', stmt_str, re.IGNORECASE):
            match_name = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`\']?([\w\.]+)["`\']?', stmt_str, re.IGNORECASE)
            if not match_name:
                continue
            table_name = match_name.group(1).split('.')[-1]
            
            content_match = re.search(r'\((.*)\)', stmt_str, re.IGNORECASE | re.DOTALL)
            if not content_match:
                continue
                
            columns_str = content_match.group(1)
            col_defs = re.split(r',\s*(?![^\(\)]*\))', columns_str)
            
            columns = []
            for col_def in col_defs:
                col_def = col_def.replace('\n', ' ').strip()
                if not col_def:
                    continue
                if re.match(r'^(PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CONSTRAINT)', col_def, re.IGNORECASE):
                    continue
                    
                parts = col_def.split()
                if len(parts) >= 2:
                    col_name = parts[0].strip('"`\'')
                    col_type_str = parts[1].split('(')[0].upper()
                    
                    if col_type_str in ('INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT'):
                        datatype = 'int'
                    elif col_type_str in ('FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC', 'REAL'):
                        datatype = 'float'
                    else:
                        datatype = 'text'
                    
                    is_pk = bool(re.search(r'PRIMARY\s+KEY', col_def, re.IGNORECASE))
                    is_fk = bool(re.search(r'REFERENCES\s+', col_def, re.IGNORECASE))
                    fk_ref = None
                    if is_fk:
                        fk_match = re.search(r'REFERENCES\s+["`\']?([\w\.]+)["`\']?\s*\(\s*["`\']?([\w]+)["`\']?\s*\)', col_def, re.IGNORECASE)
                        if fk_match:
                            fk_ref = f"{fk_match.group(1).split('.')[-1]}.{fk_match.group(2)}"
                    
                    columns.append(Column(col_name, datatype, is_pk=is_pk, is_fk=is_fk, fk_ref=fk_ref))
            
            if columns:
                tables.append(Table(table_name, columns))
                
    return DatabaseSchema(default_name, tables)

# Models
class QueryRequest(BaseModel):
    query: str

class TokenInfo(BaseModel):
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    ent_type: str
    gsql_tag: Optional[str] = None
    meta_match: Optional[Dict[str, Any]] = None

class TranslationResponse(BaseModel):
    original_query: str
    sql: str
    tokens: List[Dict[str, Any]]
    query_structure: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Welcome to G-SQL API"}

@app.get("/api/schema")
def get_schema():
    return schema.to_dict()

@app.get("/api/schemas/history")
def get_schemas_history():
    return {
        "active": active_schema_name,
        "available": list(schema_history.keys())
    }

class SchemaSwitchRequest(BaseModel):
    name: str

@app.post("/api/schema/switch")
def switch_schema(req: SchemaSwitchRequest):
    global active_schema_name, schema
    if req.name not in schema_history:
        raise HTTPException(status_code=404, detail="Database not found in history.")
    
    active_schema_name = req.name
    schema = schema_history[req.name]
    initialize_components(schema)
    return {"message": f"Switched active database to '{req.name}'", "schema": schema.to_dict()}

@app.post("/api/translate", response_model=TranslationResponse)
def translate_query(request: QueryRequest):
    try:
        # Step 2: NLP
        tokens = nlp.process(request.query)
        
        # Step 3: Tagging
        tagged_tokens = tagger.tag(tokens)
        
        # Step 4-6: Linking
        query_structure = linker.link(tagged_tokens)
        
        # Step 8: Generation
        sql = generator.generate(query_structure)
        
        # Prepare response with intermediate steps for visualization
        # Convert sets to lists for JSON serialization
        serializable_structure = {
            "select": query_structure["select"],
            "from": list(query_structure["from"]),
            "where": query_structure["where"],
            "group_by": query_structure["group_by"],
            "order_by": query_structure["order_by"],
            "limit": query_structure["limit"],
            "joins": query_structure.get("joins", [])
        }
        
        return {
            "original_query": request.query,
            "sql": sql,
            "tokens": tagged_tokens,
            "query_structure": serializable_structure
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Linker and Tagger need to be re-initialized when schema changes
def initialize_components(new_schema: DatabaseSchema):
    global schema, domain_dict, tagger, linker, generator, active_schema_name
    schema = new_schema
    if schema.name not in schema_history:
        schema_history[schema.name] = schema
    active_schema_name = schema.name
    
    # Auto-generate domain dictionary from schema
    # In a real app, successful schema upload might include domain terms
    domain_dict = DomainDictionary()
    for table in schema.tables:
        domain_dict.add_synonym(table.name.lower(), "table", table.name)
        for col in table.columns:
            domain_dict.add_synonym(col.name.lower(), "column", f"{table.name}.{col.name}")
            
    # Re-initialize components
    tagger = SemanticTagger(schema, domain_dict)
    linker = SchemaLinker(schema)
    generator = SQLGenerator()

@app.post("/api/schema/update")
def update_schema(schema_data: Dict[str, Any]):
    try:
        new_schema = DatabaseSchema.from_dict(schema_data)
        initialize_components(new_schema)
        return {"message": "Schema updated successfully", "schema": new_schema.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid schema format: {str(e)}")

@app.post("/api/schema/upload_csv")
async def upload_csv_schema(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text_content = contents.decode("utf-8")
        
        # Parse CSV
        csv_reader = csv.reader(io.StringIO(text_content))
        headers = next(csv_reader, None)
        if not headers:
            raise ValueError("CSV file is empty or missing headers")
            
        first_row = next(csv_reader, None)
        
        # Infer table name from filename
        table_name = os.path.splitext(file.filename)[0].capitalize()
        
        # Infer columns and types
        columns = []
        for idx, col_name in enumerate(headers):
            datatype = "text"
            is_pk = (idx == 0) # Assume first column is PK
            
            if first_row and len(first_row) > idx:
                val = first_row[idx].strip()
                if val.isdigit():
                    datatype = "int"
                else:
                    try:
                        float(val)
                        datatype = "float"
                    except ValueError:
                        datatype = "text"
            
            columns.append(Column(col_name.strip(), datatype, is_pk=is_pk))
            
        new_table = Table(table_name, columns)
        
        # Check if table already exists and update, or else append
        existing_table_idx = next((i for i, t in enumerate(schema.tables) if t.name.lower() == table_name.lower()), None)
        if existing_table_idx is not None:
            schema.tables[existing_table_idx] = new_table
        else:
            schema.tables.append(new_table)
            
        # Re-initialize with the updated schema
        initialize_components(schema)
        
        return {"message": f"Table '{table_name}' imported successfully from CSV", "schema": schema.to_dict()}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

@app.post("/api/schema/upload_sql")
async def upload_sql_schema(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        sql_text = contents.decode("utf-8")
        
        db_name = os.path.splitext(file.filename)[0].capitalize()
        new_schema = parse_sql_ddl(sql_text, db_name)
        
        if not new_schema.tables:
            raise ValueError("No valid CREATE TABLE statements found in SQL file.")
            
        initialize_components(new_schema)
        
        return {"message": f"SQL database '{db_name}' imported successfully", "schema": schema.to_dict()}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process SQL: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
