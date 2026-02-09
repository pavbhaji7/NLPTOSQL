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

        for i, token in enumerate(tagged_tokens):
            tag = token.get("gsql_tag")
            
            if tag == "Meta" and token.get("meta_match", {}).get("type") == "column":
                last_column = token["meta_match"]
            
            elif tag == "Value":
                # Value found. Link to last column.
                val = token["text"]
                if last_column:
                    if "table" in last_column:
                         col_str = f"{last_column['table']}.{last_column['name']}"
                    else:
                         col_str = last_column['name'] # Assumes fully qualified name like Table.Column

                    # Check for condition operator in previous tokens
                    op = "="
                    if i > 0 and tagged_tokens[i-1].get("gsql_tag") == "Cond":
                        op_token = tagged_tokens[i-1]["lemma"]
                        if op_token in [">", "<", ">=", "<=", "=", "!="]:
                             op = op_token
                        elif op_token == "after": op = ">"
                        elif op_token == "before": op = "<"
                    
                    if "table" in last_column:
                        table_name = last_column['table']
                    else:
                        table_name = last_column['name'].split('.')[0]

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
