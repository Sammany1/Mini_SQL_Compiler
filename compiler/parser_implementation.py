from .tokens import TokenType

# ========================================
# Parse Tree Node Classes
# ========================================

class ParseTreeNode:
    """Base class for all parse tree nodes."""
    def __init__(self, node_type):
        self.node_type = node_type
        self.children = []
    
    def add_child(self, child):
        """Add a child node to this node."""
        if child is not None:
            self.children.append(child)
    
    def __repr__(self):
        return f"{self.node_type}"
    
    def to_string(self, indent=0):
        """Generate a string representation of the tree."""
        result = "  " * indent + str(self) + "\n"
        for child in self.children:
            if isinstance(child, ParseTreeNode):
                result += child.to_string(indent + 1)
            else:
                result += "  " * (indent + 1) + str(child) + "\n"
        return result


class ProgramNode(ParseTreeNode):
    def __init__(self):
        super().__init__("Program")
        self.statements = []
    
    def add_statement(self, stmt):
        self.statements.append(stmt)
        self.add_child(stmt)


class SelectStatementNode(ParseTreeNode):
    def __init__(self):
        super().__init__("SelectStatement")
        self.select_list = None
        self.table_name = None
        self.where_clause = None


class InsertStatementNode(ParseTreeNode):
    def __init__(self):
        super().__init__("InsertStatement")
        self.table_name = None
        self.values = []


class UpdateStatementNode(ParseTreeNode):
    def __init__(self):
        super().__init__("UpdateStatement")
        self.table_name = None
        self.assignments = []
        self.where_clause = None


class DeleteStatementNode(ParseTreeNode):
    def __init__(self):
        super().__init__("DeleteStatement")
        self.table_name = None
        self.where_clause = None


class CreateTableStatementNode(ParseTreeNode):
    def __init__(self):
        super().__init__("CreateTableStatement")
        self.table_name = None
        self.column_defs = []


class ColumnDefNode(ParseTreeNode):
    def __init__(self, name, data_type):
        super().__init__("ColumnDef")
        self.name = name
        self.data_type = data_type
    
    def __repr__(self):
        return f"ColumnDef({self.name}: {self.data_type})"


class IdentifierNode(ParseTreeNode):
    def __init__(self, name):
        super().__init__("Identifier")
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


class LiteralNode(ParseTreeNode):
    def __init__(self, value, literal_type):
        super().__init__("Literal")
        self.value = value
        self.literal_type = literal_type
    
    def __repr__(self):
        return f"Literal({self.literal_type}: {self.value})"


class BinaryOpNode(ParseTreeNode):
    def __init__(self, operator, left, right):
        super().__init__("BinaryOp")
        self.operator = operator
        self.left = left
        self.right = right
        self.add_child(left)
        self.add_child(right)
    
    def __repr__(self):
        return f"BinaryOp({self.operator})"


class UnaryOpNode(ParseTreeNode):
    def __init__(self, operator, operand):
        super().__init__("UnaryOp")
        self.operator = operator
        self.operand = operand
        self.add_child(operand)
    
    def __repr__(self):
        return f"UnaryOp({self.operator})"


class AssignmentNode(ParseTreeNode):
    def __init__(self, identifier, value):
        super().__init__("Assignment")
        self.identifier = identifier
        self.value = value
        self.add_child(identifier)
        self.add_child(value)


# ========================================
# Parser Class
# ========================================

class Parser:
    """
    Syntax Analyzer for SQL-like language.
    Uses Recursive Descent Parsing technique.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def is_at_end(self):
        """Check if we've reached the end of tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        """Look at current token without consuming it."""
        return self.tokens[self.current]
    
    def previous(self):
        """Return the previously consumed token."""
        return self.tokens[self.current - 1]
    
    def advance(self):
        """Consume and return the current token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type):
        """Check if current token is of given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *token_types):
        """Check if current token matches any of the given types."""
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type, error_message):
        """
        Consume a token of the expected type, or report an error.
        This is crucial for error handling.
        """
        if self.check(token_type):
            return self.advance()
        
        # Report error with detailed information
        current_token = self.peek()
        self.report_error(
            current_token.line,
            current_token.column,
            f"{error_message}. Found '{current_token.lexeme}' ({current_token.type.name})"
        )
        raise ParseError()
    
    def report_error(self, line, column, message):
        """Report a syntax error."""
        error_msg = f"[Line {line}, Col {column}] Syntax Error: {message}"
        self.errors.append(error_msg)
        print(error_msg)
    
    def synchronize(self):
        """
        Error recovery mechanism (Panic Mode).
        Skip tokens until we find a synchronization point.
        """
        self.advance()
        
        while not self.is_at_end():
            # Semicolon marks end of statement - good sync point
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            # Major keywords are good sync points
            if self.peek().type in [
                TokenType.SELECT, TokenType.INSERT, TokenType.UPDATE,
                TokenType.DELETE, TokenType.CREATE
            ]:
                return
            
            self.advance()
    
    # ========================================
    # Main Parsing Entry Point
    # ========================================
    
    def parse(self):
        """
        Parse the entire program.
        Returns a ProgramNode containing all statements.
        """
        program = ProgramNode()
        
        while not self.is_at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    program.add_statement(stmt)
            except ParseError:
                # Error already reported, try to recover
                self.synchronize()
        
        return program
    
    # ========================================
    # Statement Parsing
    # ========================================
    
    def parse_statement(self):
        """Parse any SQL statement."""
        try:
            if self.match(TokenType.SELECT):
                return self.parse_select_statement()
            elif self.match(TokenType.INSERT):
                return self.parse_insert_statement()
            elif self.match(TokenType.UPDATE):
                return self.parse_update_statement()
            elif self.match(TokenType.DELETE):
                return self.parse_delete_statement()
            elif self.match(TokenType.CREATE):
                return self.parse_create_table_statement()
            else:
                current = self.peek()
                self.report_error(
                    current.line,
                    current.column,
                    f"Expected statement keyword (SELECT, INSERT, UPDATE, DELETE, CREATE), found '{current.lexeme}'"
                )
                raise ParseError()
        except ParseError:
            return None
    
    def parse_select_statement(self):
        """Parse: SELECT SelectList FROM Identifier [WHERE Condition] SEMICOLON"""
        node = SelectStatementNode()
        node.add_child(ParseTreeNode("SELECT"))
        
        # Parse select list
        select_list = self.parse_select_list()
        node.select_list = select_list
        node.add_child(select_list)
        
        # Expect FROM
        self.consume(TokenType.FROM, "Expected 'FROM' after select list")
        node.add_child(ParseTreeNode("FROM"))
        
        # Parse table name
        table_name = self.parse_identifier()
        node.table_name = table_name
        node.add_child(table_name)
        
        # Optional WHERE clause
        if self.match(TokenType.WHERE):
            node.add_child(ParseTreeNode("WHERE"))
            where_clause = self.parse_condition()
            node.where_clause = where_clause
            node.add_child(where_clause)
        
        # Expect SEMICOLON
        self.consume(TokenType.SEMICOLON, "Expected ';' at end of SELECT statement")
        node.add_child(ParseTreeNode("SEMICOLON"))
        
        return node
    
    def parse_insert_statement(self):
        """Parse: INSERT INTO Identifier VALUES ValueList SEMICOLON"""
        node = InsertStatementNode()
        node.add_child(ParseTreeNode("INSERT"))
        
        # Expect INTO
        self.consume(TokenType.INTO, "Expected 'INTO' after INSERT")
        node.add_child(ParseTreeNode("INTO"))
        
        # Parse table name
        table_name = self.parse_identifier()
        node.table_name = table_name
        node.add_child(table_name)
        
        # Expect VALUES
        self.consume(TokenType.VALUES, "Expected 'VALUES' after table name")
        node.add_child(ParseTreeNode("VALUES"))
        
        # Parse value list
        values = self.parse_value_list()
        node.values = values
        for val in values:
            node.add_child(val)
        
        # Expect SEMICOLON
        self.consume(TokenType.SEMICOLON, "Expected ';' at end of INSERT statement")
        node.add_child(ParseTreeNode("SEMICOLON"))
        
        return node
    
    def parse_update_statement(self):
        """Parse: UPDATE Identifier SET AssignmentList [WHERE Condition] SEMICOLON"""
        node = UpdateStatementNode()
        node.add_child(ParseTreeNode("UPDATE"))
        
        # Parse table name
        table_name = self.parse_identifier()
        node.table_name = table_name
        node.add_child(table_name)
        
        # Expect SET
        self.consume(TokenType.SET, "Expected 'SET' after table name in UPDATE")
        node.add_child(ParseTreeNode("SET"))
        
        # Parse assignment list
        assignments = self.parse_assignment_list()
        node.assignments = assignments
        for assign in assignments:
            node.add_child(assign)
        
        # Optional WHERE clause
        if self.match(TokenType.WHERE):
            node.add_child(ParseTreeNode("WHERE"))
            where_clause = self.parse_condition()
            node.where_clause = where_clause
            node.add_child(where_clause)
        
        # Expect SEMICOLON
        self.consume(TokenType.SEMICOLON, "Expected ';' at end of UPDATE statement")
        node.add_child(ParseTreeNode("SEMICOLON"))
        
        return node
    
    def parse_delete_statement(self):
        """Parse: DELETE FROM Identifier [WHERE Condition] SEMICOLON"""
        node = DeleteStatementNode()
        node.add_child(ParseTreeNode("DELETE"))
        
        # Expect FROM
        self.consume(TokenType.FROM, "Expected 'FROM' after DELETE")
        node.add_child(ParseTreeNode("FROM"))
        
        # Parse table name
        table_name = self.parse_identifier()
        node.table_name = table_name
        node.add_child(table_name)
        
        # Optional WHERE clause
        if self.match(TokenType.WHERE):
            node.add_child(ParseTreeNode("WHERE"))
            where_clause = self.parse_condition()
            node.where_clause = where_clause
            node.add_child(where_clause)
        
        # Expect SEMICOLON
        self.consume(TokenType.SEMICOLON, "Expected ';' at end of DELETE statement")
        node.add_child(ParseTreeNode("SEMICOLON"))
        
        return node
    
    def parse_create_table_statement(self):
        """Parse: CREATE TABLE Identifier LEFT_PAREN ColumnDefList RIGHT_PAREN SEMICOLON"""
        node = CreateTableStatementNode()
        node.add_child(ParseTreeNode("CREATE"))
        
        # Expect TABLE
        self.consume(TokenType.TABLE, "Expected 'TABLE' after CREATE")
        node.add_child(ParseTreeNode("TABLE"))
        
        # Parse table name
        table_name = self.parse_identifier()
        node.table_name = table_name
        node.add_child(table_name)
        
        # Expect LEFT_PAREN
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after table name")
        node.add_child(ParseTreeNode("LEFT_PAREN"))
        
        # Parse column definitions
        column_defs = self.parse_column_def_list()
        node.column_defs = column_defs
        for col_def in column_defs:
            node.add_child(col_def)
        
        # Expect RIGHT_PAREN
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after column definitions")
        node.add_child(ParseTreeNode("RIGHT_PAREN"))
        
        # Expect SEMICOLON
        self.consume(TokenType.SEMICOLON, "Expected ';' at end of CREATE TABLE statement")
        node.add_child(ParseTreeNode("SEMICOLON"))
        
        return node
    
    # ========================================
    # Component Parsing Methods
    # ========================================
    
    def parse_select_list(self):
        """Parse: STAR | ColumnList"""
        list_node = ParseTreeNode("SelectList")
        
        if self.match(TokenType.STAR):
            star_node = ParseTreeNode("STAR")
            list_node.add_child(star_node)
        else:
            columns = self.parse_column_list()
            for col in columns:
                list_node.add_child(col)
        
        return list_node
    
    def parse_column_list(self):
        """Parse: Identifier (COMMA Identifier)*"""
        columns = []
        
        # First identifier
        columns.append(self.parse_identifier())
        
        # Additional identifiers separated by commas
        while self.match(TokenType.COMMA):
            columns.append(self.parse_identifier())
        
        return columns
    
    def parse_value_list(self):
        """Parse: LEFT_PAREN Value (COMMA Value)* RIGHT_PAREN"""
        values = []
        
        # Expect LEFT_PAREN
        self.consume(TokenType.LEFT_PAREN, "Expected '(' before values")
        
        # First value
        values.append(self.parse_value())
        
        # Additional values separated by commas
        while self.match(TokenType.COMMA):
            values.append(self.parse_value())
        
        # Expect RIGHT_PAREN
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after values")
        
        return values
    
    def parse_value(self):
        """Parse: NUMBER | STRING | Identifier"""
        if self.check(TokenType.NUMBER):
            token = self.advance()
            return LiteralNode(token.lexeme, "NUMBER")
        elif self.check(TokenType.STRING):
            token = self.advance()
            return LiteralNode(token.lexeme, "STRING")
        elif self.check(TokenType.IDENTIFIER):
            return self.parse_identifier()
        else:
            current = self.peek()
            self.report_error(
                current.line,
                current.column,
                f"Expected value (number, string, or identifier), found '{current.lexeme}'"
            )
            raise ParseError()
    
    def parse_assignment_list(self):
        """Parse: Assignment (COMMA Assignment)*"""
        assignments = []
        
        # First assignment
        assignments.append(self.parse_assignment())
        
        # Additional assignments separated by commas
        while self.match(TokenType.COMMA):
            assignments.append(self.parse_assignment())
        
        return assignments
    
    def parse_assignment(self):
        """Parse: Identifier EQUAL Value"""
        identifier = self.parse_identifier()
        
        self.consume(TokenType.EQUAL, "Expected '=' in assignment")
        
        value = self.parse_value()
        
        return AssignmentNode(identifier, value)
    
    def parse_column_def_list(self):
        """Parse: ColumnDef (COMMA ColumnDef)*"""
        column_defs = []
        
        # First column definition
        column_defs.append(self.parse_column_def())
        
        # Additional column definitions separated by commas
        while self.match(TokenType.COMMA):
            column_defs.append(self.parse_column_def())
        
        return column_defs
    
    def parse_column_def(self):
        """Parse: Identifier TYPE"""
        name_token = self.consume(TokenType.IDENTIFIER, "Expected column name")
        name = name_token.lexeme
        
        type_token = self.consume(TokenType.TYPE, "Expected data type (INT, FLOAT, TEXT)")
        data_type = type_token.lexeme
        
        return ColumnDefNode(name, data_type)
    
    def parse_identifier(self):
        """Parse: IDENTIFIER"""
        token = self.consume(TokenType.IDENTIFIER, "Expected identifier")
        return IdentifierNode(token.lexeme)
    
    # ========================================
    # Condition Parsing (The Tricky Part!)
    # ========================================
    
    def parse_condition(self):
        """
        Parse: OrCondition
        This is the entry point for condition parsing.
        """
        return self.parse_or_condition()
    
    def parse_or_condition(self):
        """
        Parse: AndCondition (OR AndCondition)*
        OR has lowest precedence.
        """
        left = self.parse_and_condition()
        
        while self.match(TokenType.OR):
            operator = "OR"
            right = self.parse_and_condition()
            left = BinaryOpNode(operator, left, right)
        
        return left
    
    def parse_and_condition(self):
        """
        Parse: NotCondition (AND NotCondition)*
        AND has higher precedence than OR.
        """
        left = self.parse_not_condition()
        
        while self.match(TokenType.AND):
            operator = "AND"
            right = self.parse_not_condition()
            left = BinaryOpNode(operator, left, right)
        
        return left
    
    def parse_not_condition(self):
        """
        Parse: [NOT] PrimaryCondition
        NOT has highest precedence.
        """
        if self.match(TokenType.NOT):
            operator = "NOT"
            operand = self.parse_primary_condition()
            return UnaryOpNode(operator, operand)
        
        return self.parse_primary_condition()
    
    def parse_primary_condition(self):
        """
        Parse: LEFT_PAREN Condition RIGHT_PAREN | Comparison
        Base case for conditions - either a grouped condition or a comparison.
        """
        # Check for parenthesized condition
        if self.match(TokenType.LEFT_PAREN):
            condition = self.parse_condition()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
            return condition
        
        # Otherwise, parse a comparison
        return self.parse_comparison()
    
    def parse_comparison(self):
        """
        Parse: Identifier ComparisonOp Value
        """
        left = self.parse_identifier()
        
        # Parse comparison operator
        operator = None
        if self.match(TokenType.EQUAL):
            operator = "="
        elif self.match(TokenType.NOT_EQUAL):
            operator = "!="
        elif self.match(TokenType.LESS_THAN):
            operator = "<"
        elif self.match(TokenType.LESS_EQUAL):
            operator = "<="
        elif self.match(TokenType.GREATER_THAN):
            operator = ">"
        elif self.match(TokenType.GREATER_EQUAL):
            operator = ">="
        else:
            current = self.peek()
            self.report_error(
                current.line,
                current.column,
                f"Expected comparison operator (=, !=, <, <=, >, >=), found '{current.lexeme}'"
            )
            raise ParseError()
        
        right = self.parse_value()
        
        return BinaryOpNode(operator, left, right)


# ========================================
# Custom Exception for Parse Errors
# ========================================

class ParseError(Exception):
    """Exception raised during parsing to trigger error recovery."""
    pass
