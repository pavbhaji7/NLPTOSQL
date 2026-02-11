from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

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

schema, domain_dict = create_sample_schema()

try:
    nlp = NLPProcessor()
except OSError:
    print("Spacy model not found. Downloading...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = NLPProcessor()

tagger = SemanticTagger(schema, domain_dict)
linker = SchemaLinker(schema)
generator = SQLGenerator()

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
    return JSONSerializer.serialize(schema)

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
