from typing import Dict, Any, List

class SQLGenerator:
    @staticmethod
    def generate(query_structure: Dict[str, Any]) -> str:
        # SELECT
        select_clause = "SELECT " + ", ".join(query_structure["select"]) if query_structure["select"] else "SELECT *"
        
        # FROM
        # We need to pick a primary table.
        # Heuristic: Pick the first one in the set, or the one that is the 'left' side of joins
        distinct_tables = list(query_structure["from"])
        if not distinct_tables:
            return "" # Error or empty
        
        primary_table = distinct_tables[0]
        from_clause = f"FROM {primary_table}"
        
        # JOINS
        join_clause = " ".join(query_structure["joins"])
        
        # WHERE
        where_clause = "WHERE " + " AND ".join(query_structure["where"]) if query_structure["where"] else ""
        
        # GROUP BY
        group_by_clause = "GROUP BY " + ", ".join(query_structure["group_by"]) if query_structure["group_by"] else ""
        
        # ORDER BY
        order_by_clause = "ORDER BY " + ", ".join(query_structure["order_by"]) if query_structure["order_by"] else ""
        
        # LIMIT
        limit_clause = f"LIMIT {query_structure['limit']}" if query_structure["limit"] else ""
        
        # Construct final query
        parts = [select_clause, from_clause, join_clause, where_clause, group_by_clause, order_by_clause, limit_clause]
        return " ".join(part for part in parts if part).strip() + ";"
