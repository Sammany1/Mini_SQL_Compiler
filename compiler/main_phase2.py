from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.tokens import TokenType
from datetime import datetime
import os

def main():
    input_file_path = 'input.txt'
    output_dir = 'output'
    
    # Create timestamp for output filenames
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    token_output = os.path.join(output_dir, f"token_stream_{timestamp}.txt")
    parse_tree_output = os.path.join(output_dir, f"parse_tree_{timestamp}.txt")
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read input file
    try:
        with open(input_file_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file_path}'")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"=== Phase 1: Lexical Analysis ===")
    print(f"Scanning file: {input_file_path}\n")

    # ========================================
    # Phase 1: Lexical Analysis
    # ========================================
    lexer = Lexer(source_code)
    
    try:
        tokens = lexer.scan_tokens()
        
        # Write token stream to file
        with open(token_output, 'w') as f:
            f.write(f"{'Line':<5} | {'Col':<5} | {'Token Type':<15} | Lexeme\n")
            f.write("-" * 50 + "\n")
            
            for token in tokens:
                if token.type == TokenType.ILLEGAL:
                    continue
                
                token_type_str = token.type.name
                lexeme_str = repr(token.lexeme) if '\n' in token.lexeme else token.lexeme
                
                f.write(f"{token.line:<5} | {token.column:<5} | {token_type_str:<15} | {lexeme_str}\n")
        
        print(f"✓ Token stream written to: {token_output}")
        
        # Display token count
        valid_tokens = [t for t in tokens if t.type != TokenType.ILLEGAL]
        print(f"✓ Generated {len(valid_tokens)} tokens\n")
        
    except Exception as e:
        print(f"✗ Lexical analysis failed: {e}")
        return

    # ========================================
    # Phase 2: Syntax Analysis
    # ========================================
    print(f"=== Phase 2: Syntax Analysis ===")
    
    # Filter out ILLEGAL tokens for parsing
    valid_tokens = [t for t in tokens if t.type != TokenType.ILLEGAL]
    
    parser = Parser(valid_tokens)
    
    try:
        parse_tree = parser.parse()
        
        # Check if there were any syntax errors
        if parser.errors:
            print(f"\n✗ Parsing completed with {len(parser.errors)} error(s)")
            print("\nSyntax Errors:")
            for error in parser.errors:
                print(f"  {error}")
        else:
            print("✓ Parsing completed successfully - no syntax errors")
        
        # Write parse tree to file
        with open(parse_tree_output, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("PARSE TREE\n")
            f.write("=" * 60 + "\n\n")
            
            if parser.errors:
                f.write("NOTE: Parse tree generated with errors. See console for details.\n\n")
            
            f.write(parse_tree.to_string())
            
            if parser.errors:
                f.write("\n" + "=" * 60 + "\n")
                f.write("SYNTAX ERRORS DETECTED\n")
                f.write("=" * 60 + "\n\n")
                for error in parser.errors:
                    f.write(f"{error}\n")
        
        print(f"✓ Parse tree written to: {parse_tree_output}\n")
        
        # Display summary
        print("=== Summary ===")
        print(f"Statements parsed: {len(parse_tree.statements)}")
        print(f"Syntax errors: {len(parser.errors)}")
        
        # Display parse tree preview
        if parse_tree.statements:
            print("\nParse Tree Preview:")
            print("-" * 40)
            # Show first few levels of the tree
            preview = parse_tree.to_string()
            lines = preview.split('\n')[:20]  # First 20 lines
            print('\n'.join(lines))
            if len(preview.split('\n')) > 20:
                print("... (see full tree in output file)")
        
    except Exception as e:
        print(f"✗ Parsing failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
