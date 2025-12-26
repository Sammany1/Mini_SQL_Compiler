from compiler.errors import CompilerError
from compiler.ast_nodes import CreateTable, Insert, Select, CreateUser, Grant
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
            else:
                print(f"[Semantic] Warning: Unknown statement type {type(stmt)}")

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

    def visit_select(self, node):
        # 1. Check Table Exists
        if node.table_name not in self.symbol_table:
            raise CompilerError(f"Table '{node.table_name}' not found.", node.line, 0, "Semantic")
            
        table_def = self.symbol_table[node.table_name]
        
        # 2. Check Selected Columns
        for col in node.columns:
            if col != "*" and col not in table_def:
                raise CompilerError(f"Column '{col}' not found in table '{node.table_name}'.", node.line, 0, "Semantic")
                
        # 3. Check WHERE Clause (if exists)
        if node.condition:
            col_token, op, val_token = node.condition
            col_name = col_token.lexeme
            
            # Check if condition column exists
            if col_name not in table_def:
                raise CompilerError(f"Column '{col_name}' in WHERE clause not found.", col_token.line, col_token.column, "Semantic")
            
            # Check Type Compatibility
            col_type = table_def[col_name]
            is_compatible = False
            
            if col_type == 'INT' and val_token.type == TokenType.NUMBER:
                is_compatible = True
            elif col_type == 'TEXT' and val_token.type == TokenType.STRING:
                is_compatible = True
            elif col_type == 'FLOAT' and val_token.type == TokenType.NUMBER:
                is_compatible = True
                
            if not is_compatible:
                raise CompilerError(f"Type Mismatch in WHERE. Column '{col_name}' is {col_type} but compared with {val_token.type.name}.", 
                                    val_token.line, val_token.column, "Semantic")
                                    
        print(f"[Semantic] Select from '{node.table_name}' validated.")