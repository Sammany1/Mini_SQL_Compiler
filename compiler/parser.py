from compiler.tokens import TokenType
from compiler.errors import CompilerError
from compiler.ast_nodes import CreateTable, Insert, Select, CreateUser, Grant, Update, Delete

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """
        Parse all statements with error recovery.
        Uses panic mode: when an error occurs, skip tokens until a synchronizing
        token is found, then continue parsing the rest of the input.
        """
        statements = []
        while not self.is_at_end():
            try:
                statements.append(self.statement())
            except CompilerError as e:
                # Report the error
                print(f"[Syntax Error] Line {e.line}, Col {e.column}: {e.message}")
                # Try to recover by synchronizing to next statement
                self.synchronize()
        return statements
    
    def synchronize(self):
        """
        Error recovery: Skip tokens until we find a synchronizing token.
        Synchronizing tokens are: SEMICOLON, CREATE, INSERT, SELECT, UPDATE, DELETE, GRANT
        """
        self.advance()  # Skip the current token that caused the error
        
        while not self.is_at_end():
            # If we hit a semicolon, we're likely at the end of a statement
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            # If we see a statement-starting keyword, we can resume parsing
            if self.peek().type in (TokenType.CREATE, TokenType.INSERT, TokenType.SELECT,
                                   TokenType.UPDATE, TokenType.DELETE, TokenType.GRANT):
                return
            
            self.advance()

    def statement(self):
        if self.match(TokenType.CREATE):
            # Distinguish between CREATE TABLE and CREATE USER
            if self.check(TokenType.TABLE):
                return self.parse_create_table()
            elif self.check(TokenType.USER):
                return self.parse_create_user()
            else:
                 token = self.peek()
                 raise CompilerError("Expected 'TABLE' or 'USER' after CREATE", token.line, token.column, "Syntax")

        if self.match(TokenType.GRANT):
            return self.parse_grant()
            
        if self.match(TokenType.INSERT):
            return self.parse_insert()
            
        if self.match(TokenType.SELECT):
            return self.parse_select()
            
        if self.match(TokenType.UPDATE):
            return self.parse_update()
            
        if self.match(TokenType.DELETE):
            return self.parse_delete()
        
        # Error handling for unexpected tokens
        token = self.peek()
        raise CompilerError(f"Unexpected token '{token.lexeme}'", token.line, token.column, "Syntax")

    # --- Statement Parsers ---

    def parse_create_table(self):
        # Syntax: CREATE TABLE <name> ( <col> <type>, ... );
        start_token = self.previous() # The CREATE token
        self.consume(TokenType.TABLE, "Expected 'TABLE'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected table name")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after table name")
        
        columns = []
        # Parse first column
        if not self.check(TokenType.RIGHT_PAREN):
            self.parse_column_def(columns)
            # Parse subsequent columns
            while self.match(TokenType.COMMA):
                self.parse_column_def(columns)

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after column definitions")
        self.consume(TokenType.SEMICOLON, "Expected ';' after statement")
        
        return CreateTable(name_token.lexeme, columns, start_token.line)

    def parse_column_def(self, columns_list):
        # Helper to parse: name TYPE
        col_name = self.consume(TokenType.IDENTIFIER, "Expected column name").lexeme
        col_type = self.consume(TokenType.TYPE, "Expected column type (INT, TEXT, FLOAT)").lexeme
        columns_list.append((col_name, col_type))

    def parse_create_user(self):
        # Syntax: CREATE USER <name> IDENTIFIED BY <password>;
        start_token = self.previous()
        self.consume(TokenType.USER, "Expected 'USER' after CREATE")
        
        username = self.consume(TokenType.IDENTIFIER, "Expected username").lexeme
        self.consume(TokenType.IDENTIFIED, "Expected 'IDENTIFIED'")
        self.consume(TokenType.BY, "Expected 'BY'")
        
        # Password should be a string literal
        password = self.consume(TokenType.STRING, "Expected password string").lexeme
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return CreateUser(username, password, start_token.line)

    def parse_grant(self):
        # Syntax: GRANT <privilege> ON <table> TO <user>;
        start_token = self.previous()
        
        # Privilege can be a keyword (SELECT, INSERT) or Identifier
        if self.match(TokenType.SELECT, TokenType.INSERT, TokenType.UPDATE, TokenType.DELETE):
            privilege = self.previous().type.name 
        elif self.match(TokenType.IDENTIFIER):
            privilege = self.previous().lexeme.upper()
        else:
             token = self.peek()
             raise CompilerError("Expected privilege (SELECT, INSERT, etc.)", token.line, token.column, "Syntax")
             
        self.consume(TokenType.ON, "Expected 'ON'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").lexeme
        self.consume(TokenType.TO, "Expected 'TO'")
        user_name = self.consume(TokenType.IDENTIFIER, "Expected user name").lexeme
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return Grant(privilege, table_name, user_name, start_token.line)

    def parse_insert(self):
        # Syntax: INSERT INTO <table> VALUES (val1, val2, ...);
        start_token = self.previous()
        self.consume(TokenType.INTO, "Expected 'INTO' after INSERT")
        name = self.consume(TokenType.IDENTIFIER, "Expected table name").lexeme
        self.consume(TokenType.VALUES, "Expected 'VALUES'")
        self.consume(TokenType.LEFT_PAREN, "Expected '('")
        
        values = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                # We accept Number or String literals
                if self.match(TokenType.NUMBER) or self.match(TokenType.STRING):
                    values.append(self.previous()) # Keep the token for type checking
                else:
                    curr = self.peek()
                    raise CompilerError(f"Expected value, found {curr.type.name}", curr.line, curr.column, "Syntax")
                
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return Insert(name, values, start_token.line)

    def parse_select(self):
        # Syntax: SELECT <cols> FROM <table> [WHERE <condition>];
        start_token = self.previous()
        
        # 1. Parse Column List
        columns = []
        if self.match(TokenType.STAR):
            columns.append("*")
        else:
            while True:
                col_name = self.consume(TokenType.IDENTIFIER, "Expected column name").lexeme
                columns.append(col_name)
                if not self.match(TokenType.COMMA):
                    break
        
        # 2. Parse FROM
        self.consume(TokenType.FROM, "Expected 'FROM'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").lexeme
        
        # 3. Parse WHERE (Optional)
        condition = None
        if self.match(TokenType.WHERE):
            condition = self.parse_condition()
            
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return Select(table_name, columns, condition, start_token.line)

    def parse_update(self):
        # Syntax: UPDATE <table> SET <col> = <val>, ... [WHERE <condition>];
        start_token = self.previous()  # The UPDATE token
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").lexeme
        self.consume(TokenType.SET, "Expected 'SET' after table name")
        
        # Parse assignments: col1 = val1, col2 = val2, ...
        assignments = []
        while True:
            col_name = self.consume(TokenType.IDENTIFIER, "Expected column name").lexeme
            self.consume(TokenType.EQUAL, "Expected '=' after column name")
            
            # Parse value (NUMBER or STRING)
            if self.match(TokenType.NUMBER) or self.match(TokenType.STRING):
                value = self.previous()
                assignments.append((col_name, value))
            else:
                token = self.peek()
                raise CompilerError("Expected value (NUMBER or STRING)", token.line, token.column, "Syntax")
            
            if not self.match(TokenType.COMMA):
                break
        
        # Parse optional WHERE clause
        condition = None
        if self.match(TokenType.WHERE):
            condition = self.parse_condition()
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return Update(table_name, assignments, condition, start_token.line)

    def parse_delete(self):
        # Syntax: DELETE FROM <table> [WHERE <condition>];
        start_token = self.previous()  # The DELETE token
        self.consume(TokenType.FROM, "Expected 'FROM' after DELETE")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").lexeme
        
        # Parse optional WHERE clause
        condition = None
        if self.match(TokenType.WHERE):
            condition = self.parse_condition()
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return Delete(table_name, condition, start_token.line)

    def parse_condition(self):
        """
        Parse condition with support for compound conditions (AND, OR, NOT).
        Grammar: Condition -> ORCondition
        Precedence: NOT > AND > OR (implemented using precedence climbing)
        """
        return self.parse_or_condition()
    
    def parse_or_condition(self):
        """Parse OR conditions (lowest precedence)."""
        condition = self.parse_and_condition()
        
        while self.match(TokenType.OR):
            operator = self.previous().lexeme
            right = self.parse_and_condition()
            condition = ('OR', condition, right)
        
        return condition
    
    def parse_and_condition(self):
        """Parse AND conditions (medium precedence)."""
        condition = self.parse_not_condition()
        
        while self.match(TokenType.AND):
            operator = self.previous().lexeme
            right = self.parse_not_condition()
            condition = ('AND', condition, right)
        
        return condition
    
    def parse_not_condition(self):
        """Parse NOT conditions (highest precedence)."""
        if self.match(TokenType.NOT):
            operator = self.previous().lexeme
            condition = self.parse_simple_condition()
            return ('NOT', condition)
        
        return self.parse_simple_condition()
    
    def parse_simple_condition(self):
        """Parse simple comparison condition: Identifier Operator Literal."""
        # Check for Identifier
        left = self.consume(TokenType.IDENTIFIER, "Expected column in condition")
        
        # Check for Operator
        operator = None
        if self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN, 
                      TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.previous().lexeme
        else:
            token = self.peek()
            raise CompilerError("Expected comparison operator (=, <, >, etc.)", token.line, token.column, "Syntax")
            
        # Check for Value (Literal)
        right = None
        if self.match(TokenType.NUMBER) or self.match(TokenType.STRING):
            right = self.previous()
        else:
            token = self.peek()
            raise CompilerError("Expected value in comparison", token.line, token.column, "Syntax")
            
        return ('COMPARE', left, operator, right)

    # --- Utility Methods ---
    
    def match(self, *types):
        """Checks if current token matches any of the types. Consumes if yes."""
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type):
        """Checks current token type without consuming."""
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        """Consumes current token."""
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type, message):
        """Consumes expected token or raises error."""
        if self.check(type):
            return self.advance()
        token = self.peek()
        raise CompilerError(message, token.line, token.column, "Syntax")