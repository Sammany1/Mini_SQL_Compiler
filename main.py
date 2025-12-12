"""
Main entry point for the Mini SQL Compiler.
Phase 02: Syntax Analyzer (Parser)
"""

import sys
import io

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from compiler.lexer import Lexer
from compiler.parser import Parser


def get_token_display_name(token_type):
    """Convert token type to display name matching example format."""
    name_map = {
        'EQUAL': 'ASSIGN',
        'LEFT_PAREN': 'LPAR',
        'RIGHT_PAREN': 'RPAR',
        'TYPE': lambda t: t.lexeme if hasattr(t, 'lexeme') else 'TYPE',
    }
    return name_map.get(token_type.name, token_type.name)


def main():
    """Main function to run the compiler."""
    # Read input file
    try:
        with open('input.txt', 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print("Error: input.txt not found!")
        return
    
    # Phase 01: Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.scan_tokens()
    
    # Display tokens in the format: lexeme: xxx token: XXX line: X  col: X
    display_tokens = [t for t in tokens if t.type.name != 'EOF' and t.type.name != 'ILLEGAL']
    for token in display_tokens:
        token_name = get_token_display_name(token.type)
        if token.type.name == 'TYPE':
            token_name = token.lexeme  # INT, FLOAT, TEXT
        print(f"  lexeme: {token.lexeme} token: {token_name} line: {token.line}  col: {token.column}")
    
    # Show token errors (ILLEGAL tokens)
    illegal_tokens = [t for t in tokens if t.type.name == 'ILLEGAL']
    if illegal_tokens:
        print("\nToken Errors:")
        for token in illegal_tokens:
            print(f"Token error at line {token.line}, column {token.column}: illegal token")
    
    # Phase 02: Syntax Analysis
    parser = Parser(tokens)
    statements = parser.parse()
    
    # Display Parse Trees
    print("\n\n--- Phase 2: Parse Trees ---\n")
    
    if statements:
        for i, stmt in enumerate(statements, 1):
            print(f"\n--- Statement {i} ---\n")
            tree_output = stmt.to_tree_string()
            print(tree_output)
            print()
    
    # Display Syntax Errors
    if parser.errors:
        print("\nSyntax Errors:\n")
        for error in parser.errors:
            print(f"Syntax Error: {error.message}")


if __name__ == "__main__":
    main()
