from enum import Enum, auto

class TokenType(Enum):
    # --- Keywords ---
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    INSERT = auto()
    INTO = auto()
    VALUES = auto()
    UPDATE = auto()
    SET = auto()
    DELETE = auto()
    CREATE = auto()
    TABLE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # New Keywords for User/Roles
    USER = auto()
    IDENTIFIED = auto()
    BY = auto()
    GRANT = auto()
    REVOKE = auto()
    ON = auto()
    TO = auto()
    
    # --- Data types ---
    TYPE = auto() # INT, FLOAT, TEXT
    
    # --- Identifiers & Literals ---
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # --- Operators ---
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    
    # --- Delimiters ---
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    SEMICOLON = auto()
    
    # --- Special ---
    ILLEGAL = auto()
    EOF = auto()

class Token:
    """A class to represent a token found by the Lexer."""
    def __init__(self, token_type, lexeme, line, column):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        """
        Returns a string representation of the token, 
        formatted like the project sample output.
        """
        return f"Token: {self.type.name}, Lexeme: {self.lexeme}"
