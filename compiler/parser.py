"""
Syntax Analyzer (Parser) for the SQL-like language.
Implements Recursive Descent Parsing.
"""

from .tokens import TokenType
from .ast import (
    Statement, CreateTableStatement, InsertStatement, SelectStatement,
    UpdateStatement, DeleteStatement, Value, Condition, BooleanExpression
)


class SyntaxError(Exception):
    """Custom exception for syntax errors."""
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Syntax Error: {message} at line {line}, position {column}")


class Parser:
    """
    Recursive Descent Parser for SQL-like language.
    Consumes tokens from the lexer and builds a Parse Tree (AST).
    """
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.synchronize_tokens = [
            TokenType.SELECT, TokenType.INSERT, TokenType.UPDATE,
            TokenType.DELETE, TokenType.CREATE, TokenType.SEMICOLON
        ]
    
    def parse(self):
        """
        Main parsing method. Parses a sequence of statements.
        Returns a list of Statement nodes.
        """
        statements = []
        
        while not self.is_at_end():
            try:
                statement = self.statement()
                if statement:
                    statements.append(statement)
            except SyntaxError as e:
                self.errors.append(e)
                self.synchronize()
        
        return statements
    
    def statement(self):
        """Parses a single statement."""
        if self.match(TokenType.CREATE):
            return self.create_table_statement()
        elif self.match(TokenType.INSERT):
            return self.insert_statement()
        elif self.match(TokenType.SELECT):
            return self.select_statement()
        elif self.match(TokenType.UPDATE):
            return self.update_statement()
        elif self.match(TokenType.DELETE):
            return self.delete_statement()
        else:
            raise self.error(self.peek(), "Expected a statement (CREATE, INSERT, SELECT, UPDATE, DELETE)")
    
    # CREATE TABLE statement
    def create_table_statement(self):
        """Parses: CREATE TABLE table_name (column_definitions);"""
        self.consume(TokenType.TABLE, "Expected 'TABLE' after 'CREATE'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name after 'TABLE'")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after table name")
        
        columns = self.column_list()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after column definitions")
        self.consume(TokenType.SEMICOLON, "Expected ';' after CREATE TABLE statement")
        
        return CreateTableStatement(table_name.lexeme, columns)
    
    def column_list(self):
        """Parses: column_name TYPE [, column_name TYPE]*"""
        columns = []
        
        # First column definition
        col_name = self.consume(TokenType.IDENTIFIER, "Expected column name")
        col_type = self.consume(TokenType.TYPE, "Expected data type (INT, FLOAT, TEXT)")
        columns.append((col_name.lexeme, col_type.lexeme))
        
        # Additional column definitions
        while self.match(TokenType.COMMA):
            col_name = self.consume(TokenType.IDENTIFIER, "Expected column name after ','")
            col_type = self.consume(TokenType.TYPE, "Expected data type after column name")
            columns.append((col_name.lexeme, col_type.lexeme))
        
        return columns
    
    # INSERT statement
    def insert_statement(self):
        """Parses: INSERT INTO table_name VALUES (value_list);"""
        self.consume(TokenType.INTO, "Expected 'INTO' after 'INSERT'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name after 'INTO'")
        self.consume(TokenType.VALUES, "Expected 'VALUES' after table name")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'VALUES'")
        
        values = self.value_list()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after value list")
        self.consume(TokenType.SEMICOLON, "Expected ';' after INSERT statement")
        
        return InsertStatement(table_name.lexeme, values)
    
    def value_list(self):
        """Parses: value [, value]*"""
        values = []
        
        # First value
        values.append(self.value())
        
        # Additional values
        while self.match(TokenType.COMMA):
            values.append(self.value())
        
        return values
    
    def value(self):
        """Parses a single value: NUMBER | STRING | IDENTIFIER"""
        if self.match(TokenType.NUMBER):
            return Value(self.previous().lexeme, 'NUMBER')
        elif self.match(TokenType.STRING):
            return Value(self.previous().lexeme, 'STRING')
        elif self.match(TokenType.IDENTIFIER):
            return Value(self.previous().lexeme, 'IDENTIFIER')
        else:
            raise self.error(self.peek(), "Expected a value (number, string, or identifier)")
    
    # SELECT statement
    def select_statement(self):
        """Parses: SELECT select_list FROM table_name [WHERE condition];"""
        select_list = self.select_list()
        self.consume(TokenType.FROM, "Expected 'FROM' after SELECT list")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name after 'FROM'")
        
        where_clause = None
        if self.match(TokenType.WHERE):
            where_clause = self.condition()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after SELECT statement")
        
        return SelectStatement(select_list, table_name.lexeme, where_clause)
    
    def select_list(self):
        """Parses: '*' | identifier_list"""
        if self.match(TokenType.STAR):
            return ['*']
        else:
            return self.identifier_list()
    
    def identifier_list(self):
        """Parses: identifier [, identifier]*"""
        identifiers = []
        
        # First identifier
        id_token = self.consume(TokenType.IDENTIFIER, "Expected identifier in SELECT list")
        identifiers.append(id_token.lexeme)
        
        # Additional identifiers
        while self.match(TokenType.COMMA):
            id_token = self.consume(TokenType.IDENTIFIER, "Expected identifier after ','")
            identifiers.append(id_token.lexeme)
        
        return identifiers
    
    # UPDATE statement
    def update_statement(self):
        """Parses: UPDATE table_name SET assignment_list [WHERE condition];"""
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name after 'UPDATE'")
        self.consume(TokenType.SET, "Expected 'SET' after table name")
        
        assignments = self.assignment_list()
        
        where_clause = None
        if self.match(TokenType.WHERE):
            where_clause = self.condition()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after UPDATE statement")
        
        return UpdateStatement(table_name.lexeme, assignments, where_clause)
    
    def assignment_list(self):
        """Parses: column = value [, column = value]*"""
        assignments = []
        
        # First assignment
        col_name = self.consume(TokenType.IDENTIFIER, "Expected column name after 'SET'")
        self.consume(TokenType.EQUAL, "Expected '=' after column name")
        val = self.value()
        assignments.append((col_name.lexeme, val))
        
        # Additional assignments
        while self.match(TokenType.COMMA):
            col_name = self.consume(TokenType.IDENTIFIER, "Expected column name after ','")
            self.consume(TokenType.EQUAL, "Expected '=' after column name")
            val = self.value()
            assignments.append((col_name.lexeme, val))
        
        return assignments
    
    # DELETE statement
    def delete_statement(self):
        """Parses: DELETE FROM table_name [WHERE condition];"""
        self.consume(TokenType.FROM, "Expected 'FROM' after 'DELETE'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name after 'FROM'")
        
        where_clause = None
        if self.match(TokenType.WHERE):
            where_clause = self.condition()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after DELETE statement")
        
        return DeleteStatement(table_name.lexeme, where_clause)
    
    # Condition parsing (handles boolean expressions)
    def condition(self):
        """Parses a condition: handles AND, OR, NOT with proper precedence."""
        return self.or_condition()
    
    def or_condition(self):
        """Parses OR conditions (lowest precedence)."""
        expr = self.and_condition()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_condition()
            expr = BooleanExpression(expr, operator.type, right)
        
        return expr
    
    def and_condition(self):
        """Parses AND conditions (medium precedence)."""
        expr = self.not_condition()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.not_condition()
            expr = BooleanExpression(expr, operator.type, right)
        
        return expr
    
    def not_condition(self):
        """Parses NOT conditions (highest precedence)."""
        if self.match(TokenType.NOT):
            operator = self.previous()
            expr = self.comparison()
            return BooleanExpression(expr, operator.type, None)
        
        return self.comparison()
    
    def comparison(self):
        """Parses a comparison: value operator value | (condition)"""
        if self.match(TokenType.LEFT_PAREN):
            expr = self.condition()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
            return expr
        
        left = self.value()
        
        # Check for comparison operators
        if self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
                     TokenType.LESS_EQUAL, TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            operator = self.previous()
            right = self.value()
            return Condition(left, operator.type, right)
        else:
            # Single value (for cases like WHERE column)
            raise self.error(self.peek(), "Expected comparison operator (=, !=, <, <=, >, >=)")
    
    # Utility methods
    def match(self, *token_types):
        """Checks if current token matches any of the given types."""
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type):
        """Checks if current token is of the given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self):
        """Advances to the next token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        """Checks if we've consumed all tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        """Returns the current token without consuming it."""
        return self.tokens[self.current]
    
    def previous(self):
        """Returns the previously consumed token."""
        return self.tokens[self.current - 1]
    
    def consume(self, token_type, message):
        """Consumes a token of the expected type, or raises an error."""
        if self.check(token_type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token, message):
        """Creates a syntax error."""
        if token.type == TokenType.EOF:
            return SyntaxError(f"{message} (at end of file)", token.line, token.column)
        return SyntaxError(f"{message}, but found '{token.lexeme}'", token.line, token.column)
    
    def synchronize(self):
        """Error recovery: skip tokens until a synchronizing token is found."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in self.synchronize_tokens:
                return
            
            self.advance()
