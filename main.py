from compiler.lexer import Lexer
from compiler.tokens import TokenType
from datetime import datetime
import os

def main():
    input_file_path = 'input.txt'
    output_dir = 'output'
    
    # Create timestamp and output filename ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_dir, f"token_stream_{timestamp}.txt")
    
    # Ensure the output directory exists ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(input_file_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file_path}'")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"--- Scanning file: {input_file_path} ---")

    # 1. Create the Lexer
    lexer = Lexer(source_code)
    
    # 2. Scan the tokens
    try:
        tokens = lexer.scan_tokens()
        
        # Write the output to the timestamped file ---
        with open(output_filename, 'w') as f:
            # Write the table header
            f.write(f"{'Line':<5} | {'Col':<5} | {'Token Type':<15} | Lexeme\n")
            f.write("-" * 50 + "\n")
            
            # Write each token as a row in the table
            for token in tokens:
                if token.type == TokenType.ILLEGAL:
                    continue # Skip illegal tokens, error is on console
                
                token_type_str = token.type.name
                
                # Format lexeme to handle newlines for nice table alignment
                lexeme_str = repr(token.lexeme) if '\n' in token.lexeme else token.lexeme
                
                f.write(f"{token.line:<5} | {token.column:<5} | {token_type_str:<15} | {lexeme_str}\n")
        
        # Print success message to console ---
        print(f"\n--- Token Stream successfully written to: {output_filename} ---")
                
    except Exception as e:
        print(f"An unexpected error occurred during scanning: {e}")

# Run the main function
if __name__ == "__main__":
    main()