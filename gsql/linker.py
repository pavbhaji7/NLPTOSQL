from typing import List, Dict, Any, Set, Tuple, Optional
from .schema import DatabaseSchema, Table, Column

class SchemaLinker:
    def __init__(self, schema: DatabaseSchema):
        self.schema = schema

    def link(self, tagged_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Links tokens to schema elements and returns a structured query representation.
        """
        query_structure = {
            "select": [],
            "from": set(),
            "where": [],
            "group_by": [],
            "order_by": [],
            "limit": None
        }

        # 1. Name Linking (Meta tags)
        for token in tagged_tokens:
            if token.get("gsql_tag") == "Meta":
                meta_info = token.get("meta_match")
                if meta_info:
                    if meta_info["type"] == "table":
                        query_structure["from"].add(meta_info["name"])
                    elif meta_info["type"] == "column":
                        # If table is specified, use it. Else find it.
                        if "table" in meta_info:
                            table_name = meta_info["table"]
                            col_name = meta_info["name"]
                            query_structure["select"].append(f"{table_name}.{col_name}")
                            query_structure["from"].add(table_name)
                        else:
                             # Ambiguous column - simplified: take first match
                             # Real system would use context
                             pass

        # 2. Value Linking & Condition Linking
        # Heuristic: Value is linked to the nearest preceding Column or Table
        # Conditions are linked to Values
        
        last_column = None
        current_condition = None

        # Pre-process: Merge consecutive Value tokens
        # Heuristic: "Computer" (Value) + "Science" (Value) -> "Computer Science" (Value)
        merged_tokens = []
        skip_indices = set()
        for i in range(len(tagged_tokens)):
            if i in skip_indices: continue
            
            token = tagged_tokens[i]
            if token.get("gsql_tag") == "Value":
                # Check ahead
                merged_text = token["text"]
                j = i + 1
                while j < len(tagged_tokens) and tagged_tokens[j].get("gsql_tag") == "Value":
                    # STOP merging if we encounter a known condition keyword even if tagged as Value (heuristic fix)
                    # or if the next token is explicitly tagged as Cond (though loop checks tag==Value)
                    next_text = tagged_tokens[j]["text"].lower()
                    if next_text in ["above", "below", "greater", "less", "higher", "lower", "more", "than", "after", "before"]:
                        break
                    
                    merged_text += " " + tagged_tokens[j]["text"]
                    skip_indices.add(j)
                    j += 1
                
                # Update token text
                token["text"] = merged_text
                merged_tokens.append(token)
            else:
                merged_tokens.append(token)
        
        tagged_tokens = merged_tokens

        for i, token in enumerate(tagged_tokens):
            tag = token.get("gsql_tag")
            
            if tag == "Meta" and token.get("meta_match", {}).get("type") == "column":
                last_column = token["meta_match"]
            
            elif tag in ["Value", "AGG"]:
                # Value or Aggregation found. Link to last column.
                val = token["text"]
                if last_column:
                    if "table" in last_column:
                         col_str = f"{last_column['table']}.{last_column['name']}"
                    else:
                         col_str = last_column['name'] # Assumes fully qualified name like Table.Column

                    # Check for condition operator in previous tokens (look back)
                    op = "="
                    # Look back up to 6 tokens for context
                    for k in range(i-1, max(-1, i-6), -1):
                        if tagged_tokens[k].get("gsql_tag") == "Cond":
                            op_lemma = tagged_tokens[k]["lemma"]
                            if op_lemma in [">", "<", ">=", "<=", "=", "!="]:
                                op = op_lemma
                                break
                            elif op_lemma in ["after", "greater", "higher", "more", "high", "above"]: 
                                op = ">"
                                break
                            elif op_lemma in ["before", "less", "lower", "low", "below"]: 
                                op = "<"
                                break
                    
                    if "table" in last_column:
                        table_name = last_column['table']
                    else:
                        table_name = last_column['name'].split('.')[0]
                    
                    # Heuristic: If val contains "department", try to link to Departments table
                    if "department" in val.lower():
                        # Find a table with "department" in name
                        for t_name in self.schema.table_map:
                             if "department" in t_name.lower():
                                 # Set column to this table's name column (assuming it exists)
                                 # This is a specific fix for the user's case, generalizing needs more robust entity linking
                                 col_str = f"{t_name}.name"
                                 table_name = t_name
                                 # Remove "department" from val for cleaner query usually, but keeping it is safer for exact match if DB has it
                                 # For this specific query "Computer Science department", the value is likely just "Computer Science"
                                 val = val.replace(" department", "").replace(" Department", "")
                                 break

                    # Check for aggregation (nested query)
                    # Heuristic: If value is "average", "min", "max", etc., create a subquery
                    # This is very basic; a real system would parse the phrase better
                    agg_type = None
                    if val.lower() in ["average", "avg", "mean"]: agg_type = "AVG"
                    elif val.lower() in ["minimum", "min", "lowest"]: agg_type = "MIN"
                    elif val.lower() in ["maximum", "max", "highest"]: agg_type = "MAX"
                    elif val.lower() in ["sum", "total"]: agg_type = "SUM"
                    elif val.lower() in ["count", "number"]: agg_type = "COUNT"

                    if agg_type:
                        # Subquery: SELECT AVG(col) FROM table
                        # We assume the subquery is on the same column as the condition
                        # e.g. "budget > average budget" -> budget > (SELECT AVG(budget) FROM Movie)
                        
                        subquery = {
                            "select": [f"{agg_type}({col_str})"],
                            "from": {table_name},
                            "where": [],
                            "group_by": [],
                            "order_by": [],
                            "limit": None,
                             "joins": [] 
                        }
                        query_structure["where"].append({"col": col_str, "op": op, "val": subquery})
                    else:
                        query_structure["where"].append(f"{col_str} {op} '{val}'")
                    
                    query_structure["from"].add(table_name)

        # 3. Join Inference
        # Identify all tables needed
        tables_in_query = set(query_structure["from"])
        
        # If columns from other tables are in SELECT or WHERE, add those tables
        # (This logic is implicitly handled if we add to 'from' when processing Meta/Value)

        joins = self.resolve_joins(tables_in_query)
        query_structure["joins"] = joins
        
        return query_structure

    def resolve_joins(self, tables: Set[str]) -> List[str]:
        """
        Returns a list of JOIN clauses to connect the given tables.
        Uses BFS to find paths between tables in the schema graph.
        """
        joins = []
        tables_list = list(tables)
        if len(tables_list) < 2:
            return []

        # Build adjacency graph
        adj = {}
        for t_name, table in self.schema.table_map.items():
            if t_name not in adj: adj[t_name] = []
            for col in table.columns:
                if col.is_fk and col.fk_ref:
                    ref_table, ref_col = col.fk_ref.split('.')
                    # Edge Table -> RefTable
                    adj[t_name].append((ref_table, col.name, ref_col))
                    # Edge RefTable -> Table
                    if ref_table not in adj: adj[ref_table] = []
                    adj[ref_table].append((t_name, ref_col, col.name))

        # MST-like approach: Connect all tables into one component
        # Start with first table, find path to others
        connected = {tables_list[0]}
        # We need to cover all tables in tables_list
        todo = set(tables_list[1:])
        
        while todo:
            # Find closest target in todo from any node in connected
            # For simplicity, just pick first todo and find path from any node in connected
            target = list(todo)[0]
            
            best_path = None
            
            # Run BFS from 'connected' set to 'target'
            queue = [(start_node, []) for start_node in connected]
            visited = set(connected)
            
            path_found = False
            while queue:
                current, path = queue.pop(0)
                if current == target:
                    best_path = path
                    path_found = True
                    break
                
                if current in adj:
                    for neighbor, col_from, col_to in adj[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            new_path = path + [(current, neighbor, col_from, col_to)]
                            queue.append((neighbor, new_path))
            
            if path_found and best_path:
                # Add path to joins and updated sets
                for u, v, c_u, c_v in best_path:
                    # u is already in connected (or added in previous step of path), v is new
                    if v not in connected:
                        joins.append(f"JOIN {v} ON {u}.{c_u} = {v}.{c_v}")
                        connected.add(v)
                
                if target in connected:
                    todo.remove(target)
                
                # Also remove any other todo items that are now connected
                for t in list(todo):
                    if t in connected:
                        todo.remove(t)
            else:
                # Cannot reach target
                todo.remove(target) # prevent infinite loop
                print(f"Warning: Cannot join {target} with {connected}")

        return joins
