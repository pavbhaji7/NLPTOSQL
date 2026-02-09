import sys
from gsql.schema import DatabaseSchema, Table, Column, JSONSerializer, DomainDictionary
from gsql.nlp import NLPProcessor
from gsql.tagger import SemanticTagger
from gsql.linker import SchemaLinker
from gsql.generator import SQLGenerator

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

def main():
    schema, domain_dict = create_sample_schema()
    
    # Serialize schema (just to show it works)
    # json_schema = JSONSerializer.serialize(schema)
    # print("Serialized Schema:\n", json_schema)
    
    try:
        nlp = NLPProcessor()
    except OSError:
        print("Spacy model not found. Attempting to download...")
        import os
        os.system("python -m spacy download en_core_web_sm")
        nlp = NLPProcessor()
        
    tagger = SemanticTagger(schema, domain_dict)
    linker = SchemaLinker(schema)
    generator = SQLGenerator()

    # Test queries
    queries = [
        "Find all movies released after 2000",
        "Show me the actors who played in Avatar",
        "List directors of films with budget greater than 1000000"
    ]
    
    if len(sys.argv) > 1:
        queries = [sys.argv[1]]

    print(f"{'NLQ':<50} | {'SQL'}")
    print("-" * 100)
    
    for nlq in queries:
        # Step 2: NLP
        tokens = nlp.process(nlq)
        
        # Step 3: Tagging
        tagged_tokens = tagger.tag(tokens)
        
        # Step 4-6: Linking
        query_structure = linker.link(tagged_tokens)
        
        # Step 8: Generation
        sql = generator.generate(query_structure)
        
        print(f"{nlq:<50} | {sql}")

if __name__ == "__main__":
    main()
