from .tokens import Token, TokenType

class Lexer:
    """
    The Lexical Analyzer. Reads source code and turns it into a stream
    of tokens.
    """
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.current_pos = 0
        self.line = 1
        self.column = 1
        
        # Keywords are case-sensitive [cite: 872, 875]
        self.keywords = {
            "SELECT": TokenType.SELECT,
            "FROM": TokenType.FROM,
            "WHERE": TokenType.WHERE,
            "INSERT": TokenType.INSERT,
            "INTO": TokenType.INTO,
            "VALUES": TokenType.VALUES,
            "UPDATE": TokenType.UPDATE,
            "SET": TokenType.SET,
            "DELETE": TokenType.DELETE,
            "CREATE": TokenType.CREATE,
            "TABLE": TokenType.TABLE,
            "AND": TokenType.AND,
            "OR": TokenType.OR,
            "NOT": TokenType.NOT,
            
            # Map data types to the TYPE token [cite: 877]
            "INT": TokenType.TYPE,
            "FLOAT": TokenType.TYPE,
            "TEXT": TokenType.TYPE,
        }

    def scan_tokens(self):
        """Main loop: scans all tokens from the source code."""
        while not self.is_at_end():
            self.scan_token()
        
        # Add a final EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def scan_token(self):
        """Scans and adds the next single token."""
        start_col = self.column
        start_line = self.line
        
        char = self.advance()

        # --- Single-character tokens ---
        if char == '(': self.add_token(TokenType.LEFT_PAREN, '(')
        elif char == ')': self.add_token(TokenType.RIGHT_PAREN, ')')
        elif char == ',': self.add_token(TokenType.COMMA, ',')
        elif char == ';': self.add_token(TokenType.SEMICOLON, ';')
        elif char == '*': self.add_token(TokenType.STAR, '*')
        elif char == '+': self.add_token(TokenType.PLUS, '+')
        elif char == '/': self.add_token(TokenType.SLASH, '/')
        
        # --- One or two-character tokens ---
        elif char == '=':
            self.add_token(TokenType.EQUAL, '=')
            
        elif char == '!':
            if self.peek() == '=':
                self.advance() # consume the '='
                self.add_token(TokenType.NOT_EQUAL, '!=')
            else:
                self.report_error(start_line, start_col, f"Invalid character '{char}'")

        elif char == '<':
            if self.peek() == '=':
                self.advance() # consume the '='
                self.add_token(TokenType.LESS_EQUAL, '<=')
            elif self.peek() == '>':
                self.advance() # consume the '>'
                self.add_token(TokenType.NOT_EQUAL, '<>')
            else:
                self.add_token(TokenType.LESS_THAN, '<')
                
        elif char == '>':
            if self.peek() == '=':
                self.advance() # consume the '='
                self.add_token(TokenType.GREATER_EQUAL, '>=')
            else:
                self.add_token(TokenType.GREATER_THAN, '>')

        # --- Comments [cite: 889] ---
        elif char == '-':
            if self.peek() == '-':
                self.handle_single_line_comment()
            else:
                self.add_token(TokenType.MINUS, '-')
                
        elif char == '#':
            if self.peek() == '#':
                self.handle_multiline_comment(start_line, start_col)
            else:
                self.report_error(start_line, start_col, f"Invalid character '{char}'")
                self.add_token(TokenType.ILLEGAL, char)
                
        # --- Whitespace (ignored) [cite: 870] ---
        elif char.isspace():
            pass

        # --- Multi-character tokens ---
        elif char == "'":
            self.handle_string(start_line, start_col)

        elif char.isdigit():
            self.current_pos -= 1 # Go back one to read the full number
            self.column -= 1
            self.handle_number()

        elif char.isalpha():
            self.current_pos -= 1 # Go back one to read the full identifier
            self.column -= 1
            self.handle_identifier()

        # --- Errors ---
        else:
            # Catches illegal symbols like '@' or the '$' from the sample [cite: 893-894, 909]
            self.report_error(start_line, start_col, f"Invalid character '{char}'")
            self.add_token(TokenType.ILLEGAL, char)

    # --- Helper Methods for Tokenization ---

    def handle_identifier(self):
        """Handles Identifiers and Keywords."""
        start_pos = self.current_pos
        
        # Rule: Must start with a letter [cite: 879]
        # (We already know it does from scan_token)
        
        # Rule: May contain letters, digits, or underscores [cite: 879]
        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
            
        lexeme = self.source[start_pos : self.current_pos]
        
        # Check if it's a keyword or a user-defined identifier
        token_type = self.keywords.get(lexeme, TokenType.IDENTIFIER)
        
        self.add_token(token_type, lexeme)

    def handle_number(self):
        """Handles Number literals (both INT and FLOAT)."""
        start_pos = self.current_pos
        
        # Consume all digits
        while not self.is_at_end() and self.peek().isdigit():
            self.advance()
            
        # Check for a decimal part
        if not self.is_at_end() and self.peek() == '.':
            # Consume the '.'
            self.advance()
            
            # Consume all digits after the decimal
            while not self.is_at_end() and self.peek().isdigit():
                self.advance()
                
        lexeme = self.source[start_pos : self.current_pos]
        self.add_token(TokenType.NUMBER, lexeme)

    def handle_string(self, start_line, start_col):
        """Handles String literals."""
        # We already consumed the opening '
        start_pos = self.current_pos
        
        while not self.is_at_end() and self.peek() != "'":
            self.advance()
            
        # Check for unclosed string [cite: 895-896]
        if self.is_at_end():
            self.report_error(start_line, start_col, "Unclosed string literal")
            lexeme = self.source[start_pos - 1 : self.current_pos]
            self.add_token(TokenType.ILLEGAL, lexeme)
            return

        # Consume the closing '
        self.advance() 
        
        # Get the full lexeme including quotes
        lexeme = self.source[start_pos - 1 : self.current_pos]
        self.add_token(TokenType.STRING, lexeme)

    def handle_single_line_comment(self):
        """Skips single-line comments (--)[cite: 889]."""
        # We already consumed the first '-' and peeked at the second
        self.advance() # Consume the second '-'
        
        # Keep consuming until you hit a newline or the end
        while not self.is_at_end() and self.peek() != '\n':
            self.advance()
        # We don't call add_token because comments are skipped [cite: 870]

    def handle_multiline_comment(self, start_line, start_col):
        """Skips multi-line comments (##...##)[cite: 889]."""
        # We already consumed the first '#' and peeked at the second
        self.advance() # Consume the second '#'
        
        while not self.is_at_end():
            if self.peek() == '#':
                self.advance() # consume the first '#'
                if not self.is_at_end() and self.peek() == '#':
                    self.advance() # consume the second '#'
                    return # Successfully found end of comment
            else:
                self.advance()
                
        # If we exit the loop, we're at the end of the file
        # This is an unterminated comment error [cite: 897-898]
        self.report_error(start_line, start_col, "Unterminated multi-line comment")

    # --- Utility Methods ---

    def is_at_end(self):
        """Checks if we've run out of characters."""
        return self.current_pos >= len(self.source)

    def advance(self):
        """Consumes and returns the current character, updating position."""
        char = self.source[self.current_pos]
        self.current_pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return char

    def peek(self):
        """Looks at the current character without consuming it."""
        if self.is_at_end():
            return '\0'
        return self.source[self.current_pos]

    def add_token(self, token_type, lexeme):
        """Adds a new token to the list."""
        # Calculate the starting column
        start_column = self.column - len(lexeme)
        self.tokens.append(Token(token_type, lexeme, self.line, start_column))

    def report_error(self, line, column, message):
        """
        Prints an error message with line and column numbers,
        as required by the project spec [cite: 893, 900-902].
        """
        print(f"[Line {line}, Col {column}] Error: {message}")