
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from gsql.schema import DatabaseSchema, Table, Column, DomainDictionary
from gsql.nlp import NLPProcessor
from gsql.tagger import SemanticTagger
from gsql.linker import SchemaLinker
from gsql.generator import SQLGenerator

def create_sample_schema():
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
    nlp = NLPProcessor()
    tagger = SemanticTagger(schema, domain_dict)
    linker = SchemaLinker(schema)
    generator = SQLGenerator()

    queries = [
        "Find all movies released after 2000",
        "Show me the actors who played in Avatar",
        "List directors of films with budget greater than 1000000"
    ]

    with open("d:/NLPTOSQL/debug_output_utf8.txt", "w", encoding="utf-8") as f:
        for q in queries:
            f.write(f"\nQuery: {q}\n")
            tokens = nlp.process(q)
            tagged = tagger.tag(tokens)
            structure = linker.link(tagged)
            sql = generator.generate(structure)
            
            f.write(f"Structure: {structure}\n")
            f.write(f"SQL: {sql}\n")

if __name__ == "__main__":
    main()
