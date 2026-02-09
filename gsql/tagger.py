from typing import List, Dict, Any, Tuple
from .schema import DatabaseSchema, DomainDictionary

class SemanticTagger:
    def __init__(self, schema: DatabaseSchema, domain_dict: DomainDictionary):
        self.schema = schema
        self.domain_dict = domain_dict
        self.agg_keywords = {"count", "sum", "avg", "average", "max", "maximum", "min", "minimum"}
        self.cond_keywords = {"greater", "less", "more", "than", "after", "before", "between", "equal", "=", ">", "<", ">=", "<=", "!="}
        self.help_keywords = {"per", "each", "group", "by", "order", "sort", "limit", "top", "bottom"}

    def tag(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tagged_tokens = []
        for token in tokens:
            tag = "Other"
            lemma = token["lemma"].lower()
            text = token["text"].lower()

            # Check Meta (Table/Column)
            # Simple check: is the lemma or text a table or column name?
            # Also check synonyms
            
            meta_match = self._check_meta(lemma) or self._check_meta(text)
            if meta_match:
                tag = "Meta"
                token["meta_match"] = meta_match
            
            # Check AGG
            elif lemma in self.agg_keywords:
                tag = "AGG"
            
            # Check Cond
            elif lemma in self.cond_keywords:
                tag = "Cond"
            
            # Check Help
            elif lemma in self.help_keywords:
                tag = "Help"
            
            # Check Value (simplified: if it's a noun/proper noun/number and not meta)
            # In a real system, we'd check against database values or use NER types
            elif token["pos"] in ["NOUN", "PROPN", "NUM"] and tag == "Other":
                # Heuristic: verify if it looks like a value
                # For now, just tag it as Value if it's not a stop word
                if not token["is_stop"]:  # Assuming 'is_stop' is available or we filter
                     tag = "Value"

            token["gsql_tag"] = tag
            tagged_tokens.append(token)
        return tagged_tokens

    def _check_meta(self, term: str) -> Any:
        # Check tables
        if term in self.schema.table_map:
            return {"type": "table", "name": term}
        
        # Check columns (search in all tables)
        for table in self.schema.tables:
            if term in table.column_map:
                return {"type": "column", "table": table.name, "name": term}
        
        # Check synonyms
        synonym = self.domain_dict.lookup(term)
        if synonym:
             return {"type": synonym[0], "name": synonym[1]}
        
        return None
