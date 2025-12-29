from compiler.errors import CompilerError
from compiler.ast_nodes import CreateTable, Insert, Select, CreateUser, Grant, Update, Delete
from compiler.tokens import TokenType

class SemanticAnalyzer:
    def __init__(self):
        # Structure: { "table_name": { "col_name": "TYPE", ... } }
        self.symbol_table = {} 
        # Structure: { "username": { "password": "...", "privileges": [("table", "action")] } }
        self.user_table = {}

    def analyze(self, statements):
        print(f"[Semantic] Starting analysis on {len(statements)} statements...")
        for stmt in statements:
            if isinstance(stmt, CreateTable):
                self.visit_create_table(stmt)
            elif isinstance(stmt, CreateUser):
                self.visit_create_user(stmt)
            elif isinstance(stmt, Grant):
                self.visit_grant(stmt)
            elif isinstance(stmt, Insert):
                self.visit_insert(stmt)
            elif isinstance(stmt, Select):
                self.visit_select(stmt)
            elif isinstance(stmt, Update):
                self.visit_update(stmt)
            elif isinstance(stmt, Delete):
                self.visit_delete(stmt)
            else:
                print(f"[Semantic] Warning: Unknown statement type {type(stmt)}")
        
        print(f"[Semantic] Analysis completed successfully. All semantic checks passed.")

    def visit_create_table(self, node):
        if node.table_name in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' already exists.", node.line, 0, "Semantic")
        
        # Build column map
        cols = {}
        for col_name, col_type in node.columns:
            if col_name in cols:
                 raise CompilerError(f"Duplicate column '{col_name}' in table '{node.table_name}'.", node.line, 0, "Semantic")
            cols[col_name] = col_type
        
        self.symbol_table[node.table_name] = cols
        print(f"[Semantic] Table '{node.table_name}' defined successfully.")

    def visit_create_user(self, node):
        if node.username in self.user_table:
             raise CompilerError(f"User '{node.username}' already exists.", node.line, 0, "Semantic")
        
        self.user_table[node.username] = {
            "password": node.password,
            "privileges": [] 
        }
        print(f"[Semantic] User '{node.username}' created.")

    def visit_grant(self, node):
        # 1. Check User Exists
        if node.user_name not in self.user_table:
             raise CompilerError(f"User '{node.user_name}' not found.", node.line, 0, "Semantic")

        # 2. Check Table Exists
        if node.table_name not in self.symbol_table:
             raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
             
        # 3. Apply Grant
        user_record = self.user_table[node.user_name]
        permission = (node.table_name, node.privilege)
        
        if permission in user_record['privileges']:
            print(f"[Semantic] Warning: User '{node.user_name}' already has {node.privilege} on {node.table_name}.")
        else:
            user_record['privileges'].append(permission)
            print(f"[Semantic] Granted {node.privilege} on '{node.table_name}' to '{node.user_name}'.")

    def visit_insert(self, node):
        # 1. Check Table Exists
        if node.table_name not in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
        
        table_def = self.symbol_table[node.table_name]
        expected_count = len(table_def)
        actual_count = len(node.values)

        # 2. Check Column Count
        if expected_count != actual_count:
            raise CompilerError(f"Column count mismatch. Expected {expected_count}, got {actual_count}.", node.line, 0, "Semantic")

        # 3. Check Data Types
        col_types = list(table_def.values()) # e.g. ['INT', 'TEXT']
        
        for i, val_token in enumerate(node.values):
            expected_type_str = col_types[i] # e.g., 'INT'
            
            # Simple type compatibility check
            is_valid = False
            if expected_type_str == 'INT' and val_token.type == TokenType.NUMBER:
                # Check if it's really an int (lexer stores number as string)
                if '.' not in val_token.lexeme:
                    is_valid = True
            elif expected_type_str == 'FLOAT' and val_token.type == TokenType.NUMBER:
                is_valid = True
            elif expected_type_str == 'TEXT' and val_token.type == TokenType.STRING:
                is_valid = True
            
            if not is_valid:
                 raise CompilerError(f"Type Mismatch at column {i+1}. Expected {expected_type_str}.", node.line, val_token.column, "Semantic")
        
        print(f"[Semantic] Insert into '{node.table_name}' validated.")

    def check_condition(self, condition, table_def):
        """
        Recursively check a condition (simple or compound) for semantic correctness.
        Returns the annotated condition with type information.
        """
        if condition is None:
            return None
            
        # Check if it's a compound condition
        if isinstance(condition, tuple) and len(condition) > 0:
            op = condition[0]
            
            if op == 'OR' or op == 'AND':
                # Binary operator: (OP, left_condition, right_condition)
                if len(condition) == 3:
                    left = self.check_condition(condition[1], table_def)
                    right = self.check_condition(condition[2], table_def)
                    return (op, left, right)
                else:
                    raise CompilerError(f"Invalid {op} condition structure.", 0, 0, "Semantic")
            
            elif op == 'NOT':
                # Unary operator: (NOT, condition)
                if len(condition) == 2:
                    inner = self.check_condition(condition[1], table_def)
                    return ('NOT', inner)
                else:
                    raise CompilerError("Invalid NOT condition structure.", 0, 0, "Semantic")
            
            elif op == 'COMPARE':
                # Simple comparison: ('COMPARE', col_token, operator, val_token)
                if len(condition) == 4:
                    col_token = condition[1]
                    operator = condition[2]
                    val_token = condition[3]
                    
                    col_name = col_token.lexeme
                    
                    # Check if column exists
                    if col_name not in table_def:
                        raise CompilerError(f"Column '{col_name}' in WHERE clause not found in table.", 
                                          col_token.line, col_token.column, "Semantic")
                    
                    # Check type compatibility
                    col_type = table_def[col_name]
                    is_compatible = False
                    
                    if col_type == 'INT' and val_token.type == TokenType.NUMBER:
                        # Check if it's really an int (no decimal point)
                        if '.' not in val_token.lexeme:
                            is_compatible = True
                    elif col_type == 'FLOAT' and val_token.type == TokenType.NUMBER:
                        is_compatible = True
                    elif col_type == 'TEXT' and val_token.type == TokenType.STRING:
                        is_compatible = True
                    
                    if not is_compatible:
                        val_type_name = val_token.type.name
                        raise CompilerError(f"Type mismatch in WHERE clause. Column '{col_name}' is {col_type} but compared with {val_type_name}.", 
                                          val_token.line, val_token.column, "Semantic")
                    
                    return ('COMPARE', col_token, operator, val_token, col_type)
            
        # If we get here, condition structure is unknown
        raise CompilerError(f"Invalid condition structure.", 0, 0, "Semantic")

    def visit_select(self, node):
        # 1. Check Table Exists
        if node.table_name not in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
            
        table_def = self.symbol_table[node.table_name]
        
        # 2. Check Selected Columns
        for col in node.columns:
            if col != "*" and col not in table_def:
                raise CompilerError(f"Column '{col}' not found in table '{node.table_name}'.", node.line, 0, "Semantic")
                
        # 3. Check WHERE Clause (if exists) - handles compound conditions
        if node.condition:
            self.check_condition(node.condition, table_def)
                                    
        print(f"[Semantic] Select from '{node.table_name}' validated.")

    def visit_update(self, node):
        # 1. Check Table Exists
        if node.table_name not in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
        
        table_def = self.symbol_table[node.table_name]
        
        # 2. Check SET assignments
        for col_name, val_token in node.assignments:
            # Check if column exists
            if col_name not in table_def:
                raise CompilerError(f"Column '{col_name}' not found in table '{node.table_name}'.", node.line, 0, "Semantic")
            
            # Check type compatibility
            col_type = table_def[col_name]
            is_compatible = False
            
            if col_type == 'INT' and val_token.type == TokenType.NUMBER:
                # Check if it's really an int (no decimal point)
                if '.' not in val_token.lexeme:
                    is_compatible = True
            elif col_type == 'FLOAT' and val_token.type == TokenType.NUMBER:
                is_compatible = True
            elif col_type == 'TEXT' and val_token.type == TokenType.STRING:
                is_compatible = True
            
            if not is_compatible:
                val_type_name = val_token.type.name
                raise CompilerError(f"Type mismatch in SET. Column '{col_name}' is {col_type} but value is {val_type_name}.", 
                                  val_token.line, val_token.column, "Semantic")
        
        # 3. Check WHERE Clause (if exists) - handles compound conditions
        if node.condition:
            self.check_condition(node.condition, table_def)
        
        print(f"[Semantic] Update on '{node.table_name}' validated.")

    def visit_delete(self, node):
        # 1. Check Table Exists
        if node.table_name not in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
        
        table_def = self.symbol_table[node.table_name]
        
        # 2. Check WHERE Clause (if exists) - handles compound conditions
        if node.condition:
            self.check_condition(node.condition, table_def)
        
        print(f"[Semantic] Delete from '{node.table_name}' validated.")
    
    def format_annotated_tree(self, statements):
        """
        Format annotated parse tree for output with semantic information.
        Returns a formatted string representation.
        """
        lines = []
        
        for i, stmt in enumerate(statements, 1):
            lines.append(f"\nStatement {i}: {stmt.__class__.__name__} (Line {stmt.line})")
            
            if isinstance(stmt, CreateTable):
                lines.append(f"  Table: {stmt.table_name}")
                lines.append(f"  Symbol Table Entry: -> Table '{stmt.table_name}' with {len(stmt.columns)} columns")
                lines.append("  Columns:")
                for col_name, col_type in stmt.columns:
                    lines.append(f"    - {col_name}: TYPE={col_type}")
            
            elif isinstance(stmt, Insert):
                lines.append(f"  Table: {stmt.table_name}")
                if stmt.table_name in self.symbol_table:
                    lines.append(f"  Symbol Table Reference: -> Table '{stmt.table_name}' exists")
                    col_types = list(self.symbol_table[stmt.table_name].values())
                    lines.append("  Values:")
                    for j, val_token in enumerate(stmt.values):
                        inferred_type = self._infer_type_from_token(val_token)
                        expected_type = col_types[j] if j < len(col_types) else 'UNKNOWN'
                        lines.append(f"    [{j+1}] Value: {val_token.lexeme}")
                        lines.append(f"         Token Type: {val_token.type.name}")
                        lines.append(f"         Inferred Type: {inferred_type}")
                        lines.append(f"         Expected Type: {expected_type}")
                        lines.append(f"         Symbol Table Link: -> Column {j+1} of table '{stmt.table_name}'")
                else:
                    lines.append(f"  Symbol Table Reference: -> ERROR: Table '{stmt.table_name}' not found")
            
            elif isinstance(stmt, Select):
                lines.append(f"  Table: {stmt.table_name}")
                if stmt.table_name in self.symbol_table:
                    lines.append(f"  Symbol Table Reference: -> Table '{stmt.table_name}' exists")
                    lines.append("  Selected Columns:")
                    for col in stmt.columns:
                        if col == '*':
                            lines.append(f"    - * (all columns)")
                            lines.append(f"      Type: ALL columns from '{stmt.table_name}'")
                        else:
                            col_type = self.symbol_table[stmt.table_name].get(col, 'UNKNOWN')
                            lines.append(f"    - {col}")
                            lines.append(f"      Type: {col_type}")
                            lines.append(f"      Symbol Table Link: -> Column '{col}' in table '{stmt.table_name}'")
                    
                    if stmt.condition:
                        lines.append("  WHERE Condition:")
                        self._format_condition(stmt.condition, stmt.table_name, lines, indent="    ")
                else:
                    lines.append(f"  Symbol Table Reference: -> ERROR: Table '{stmt.table_name}' not found")
            
            elif isinstance(stmt, Update):
                lines.append(f"  Table: {stmt.table_name}")
                if stmt.table_name in self.symbol_table:
                    lines.append(f"  Symbol Table Reference: -> Table '{stmt.table_name}' exists")
                    lines.append("  SET Assignments:")
                    for col_name, val_token in stmt.assignments:
                        col_type = self.symbol_table[stmt.table_name].get(col_name, 'UNKNOWN')
                        inferred_type = self._infer_type_from_token(val_token)
                        lines.append(f"    - {col_name} = {val_token.lexeme}")
                        lines.append(f"      Column Type: {col_type}")
                        lines.append(f"      Value Type: {inferred_type}")
                        lines.append(f"      Symbol Table Link: -> Column '{col_name}' in table '{stmt.table_name}'")
                    
                    if stmt.condition:
                        lines.append("  WHERE Condition:")
                        self._format_condition(stmt.condition, stmt.table_name, lines, indent="    ")
                else:
                    lines.append(f"  Symbol Table Reference: -> ERROR: Table '{stmt.table_name}' not found")
            
            elif isinstance(stmt, Delete):
                lines.append(f"  Table: {stmt.table_name}")
                if stmt.table_name in self.symbol_table:
                    lines.append(f"  Symbol Table Reference: -> Table '{stmt.table_name}' exists")
                    if stmt.condition:
                        lines.append("  WHERE Condition:")
                        self._format_condition(stmt.condition, stmt.table_name, lines, indent="    ")
                else:
                    lines.append(f"  Symbol Table Reference: -> ERROR: Table '{stmt.table_name}' not found")
        
        return "\n".join(lines)
    
    def _infer_type_from_token(self, token):
        """Infer data type from token."""
        if token.type == TokenType.NUMBER:
            if '.' in token.lexeme:
                return 'FLOAT'
            else:
                return 'INT'
        elif token.type == TokenType.STRING:
            return 'TEXT'
        return 'UNKNOWN'
    
    def _format_condition(self, condition, table_name, lines, indent=""):
        """Recursively format a condition for output."""
        if condition is None:
            return
        
        if isinstance(condition, tuple) and len(condition) > 0:
            op = condition[0]
            
            if op == 'OR' or op == 'AND':
                if len(condition) == 3:
                    lines.append(f"{indent}Operator: {op}")
                    lines.append(f"{indent}Left Condition:")
                    self._format_condition(condition[1], table_name, lines, indent + "  ")
                    lines.append(f"{indent}Right Condition:")
                    self._format_condition(condition[2], table_name, lines, indent + "  ")
            
            elif op == 'NOT':
                if len(condition) == 2:
                    lines.append(f"{indent}Operator: NOT")
                    lines.append(f"{indent}Condition:")
                    self._format_condition(condition[1], table_name, lines, indent + "  ")
            
            elif op == 'COMPARE':
                if len(condition) >= 4:
                    col_token = condition[1]
                    operator = condition[2]
                    val_token = condition[3]
                    
                    col_type = 'UNKNOWN'
                    if table_name in self.symbol_table:
                        col_type = self.symbol_table[table_name].get(col_token.lexeme, 'UNKNOWN')
                    
                    inferred_type = self._infer_type_from_token(val_token)
                    
                    lines.append(f"{indent}Comparison: {col_token.lexeme} {operator} {val_token.lexeme}")
                    lines.append(f"{indent}  Column: {col_token.lexeme}")
                    lines.append(f"{indent}    Type: {col_type}")
                    lines.append(f"{indent}    Symbol Table Link: -> Column '{col_token.lexeme}' in table '{table_name}'")
                    lines.append(f"{indent}  Value: {val_token.lexeme}")
                    lines.append(f"{indent}    Token Type: {val_token.type.name}")
                    lines.append(f"{indent}    Inferred Type: {inferred_type}")