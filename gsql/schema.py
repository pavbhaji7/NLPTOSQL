import json
from typing import List, Dict, Any, Optional

class Column:
    def __init__(self, name: str, datatype: str, is_pk: bool = False, is_fk: bool = False, fk_ref: str = None, values: List[str] = None):
        self.name = name
        self.datatype = datatype
        self.is_pk = is_pk
        self.is_fk = is_fk
        self.fk_ref = fk_ref
        self.values = values if values else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "datatype": self.datatype,
            "is_pk": self.is_pk,
            "is_fk": self.is_fk,
            "fk_ref": self.fk_ref,
            "values": self.values
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        return cls(
            name=data["name"],
            datatype=data["datatype"],
            is_pk=data.get("is_pk", False),
            is_fk=data.get("is_fk", False),
            fk_ref=data.get("fk_ref"),
            values=data.get("values")
        )

class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = columns
        self.column_map = {col.name: col for col in columns}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        columns = [Column.from_dict(col_data) for col_data in data["columns"]]
        return cls(name=data["name"], columns=columns)

class DatabaseSchema:
    def __init__(self, name: str, tables: List[Table]):
        self.name = name
        self.tables = tables
        self.table_map = {table.name: table for table in tables}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "database": self.name,
            "tables": [table.to_dict() for table in self.tables]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseSchema':
        # data might be {"database": "name", "tables": [...]} or just {"name": "name", "tables": [...]}
        name = data.get("database") or data.get("name", "UnknownDB")
        tables = [Table.from_dict(table_data) for table_data in data["tables"]]
        return cls(name=name, tables=tables)

class JSONSerializer:
    @staticmethod
    def serialize(schema: DatabaseSchema) -> str:
        return json.dumps(schema.to_dict(), indent=4)

class DomainDictionary:
    def __init__(self):
        # Allow synonyms for tables and columns
        # Format: {"synonym": ("table", "table_name") or ("column", "table_name.column_name")}
        self.synonyms: Dict[str, tuple] = {}
    
    def add_synonym(self, synonym: str, target_type: str, target_name: str):
        self.synonyms[synonym.lower()] = (target_type, target_name)

    def lookup(self, term: str) -> Optional[tuple]:
        return self.synonyms.get(term.lower())
