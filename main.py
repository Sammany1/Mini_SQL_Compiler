import os
import sys
import datetime
import io
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantics import SemanticAnalyzer
from compiler.errors import CompilerError
from compiler.tokens import TokenType

def main():
    # --- 1. Setup Input & Output Directories ---
    input_path = 'input.txt'
    
    # Create a timestamped folder for this run to avoid collisions
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("outputs", f"Run_{timestamp}")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Define file paths for each phase
    lexical_file_path = os.path.join(output_dir, "1_Lexical_Analysis.txt")
    syntax_file_path = os.path.join(output_dir, "2_Syntax_Analysis.txt")
    semantic_file_path = os.path.join(output_dir, "3_Semantic_Analysis.txt")
    
    print(f"--- Starting Compilation Run: {timestamp} ---")
    print(f"Output Folder: {output_dir}")

    # Read Input File
    try:
        with open(input_path, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: '{input_path}' not found. Please ensure the file exists.")
        return

    # Variables to hold data passed between phases
    tokens = []
    parse_tree = []
    
    # --- PHASE 1: LEXICAL ANALYSIS ---
    print(">> Running Phase 1: Lexical Analysis...")
    lexer = None
    try:
        with open(lexical_file_path, 'w') as f:
            f.write("=== PHASE 1: LEXICAL ANALYSIS (TOKEN STREAM) ===\n")
            f.write(f"{'Line':<5} | {'Col':<5} | {'Type':<15} | {'Lexeme'}\n")
            f.write("-" * 50 + "\n")

            lexer = Lexer(source)
            tokens = lexer.scan_tokens()

            for t in tokens:
                # Write to file
                f.write(f"{t.line:<5} | {t.column:<5} | {t.type.name:<15} | {t.lexeme}\n")
                
                # Check for ILLEGAL tokens (Lexical Errors)
                if t.type == TokenType.ILLEGAL:
                    raise CompilerError(f"Illegal character '{t.lexeme}' detected.", t.line, t.column, "Lexical")

            f.write("\nLexical Analysis Passed Successfully.\n")
            print("   Phase 1 Completed. Output saved.")

    except CompilerError as e:
        # Write the tokens that were scanned before the error
        if lexer and lexer.tokens:
            with open(lexical_file_path, 'w') as f:
                f.write("=== PHASE 1: LEXICAL ANALYSIS (TOKEN STREAM) ===\n")
                f.write(f"{'Line':<5} | {'Col':<5} | {'Type':<15} | {'Lexeme'}\n")
                f.write("-" * 50 + "\n")
                for t in lexer.tokens:
                    f.write(f"{t.line:<5} | {t.column:<5} | {t.type.name:<15} | {t.lexeme}\n")
                f.write(f"\n[FATAL ERROR] {e}\n")
        else:
            # No tokens were scanned, just write the error
            with open(lexical_file_path, 'a') as f:
                f.write(f"\n[FATAL ERROR] {e}\n")
        print(f"   X Phase 1 Failed! See '{lexical_file_path}' for details.")
        print(">> Compilation Stopped.")
        return # STOP PROCESS

    # --- PHASE 2: SYNTAX ANALYSIS ---
    print(">> Running Phase 2: Syntax Analysis...")
    try:
        # Capture syntax errors that parser prints
        syntax_error_capture = io.StringIO()
        original_stdout_phase2 = sys.stdout
        
        with open(syntax_file_path, 'w') as f:
            f.write("=== PHASE 2: SYNTAX ANALYSIS (PARSE TREE) ===\n\n")
            
            # Redirect stdout to capture syntax errors
            sys.stdout = syntax_error_capture
            
            parser = Parser(tokens)
            parse_tree = parser.parse()
            
            # Restore stdout
            sys.stdout = original_stdout_phase2
            
            # Write any syntax errors that occurred (from error recovery)
            error_output = syntax_error_capture.getvalue()
            if error_output:
                f.write("--- Syntax Errors (Recovered) ---\n")
                f.write(error_output)
                f.write("\n")
            
            # Write formatted Parse Tree
            if parse_tree:
                for i, node in enumerate(parse_tree):
                    f.write(f"Statement {i+1}: {node.__class__.__name__}\n")
                    if hasattr(node, '__dict__'):
                        for key, value in vars(node).items():
                            # Basic formatting for clearer output
                            f.write(f"    - {key}: {value}\n")
                    f.write("\n")
            else:
                f.write("(No statements successfully parsed)\n")

            f.write("Syntax Analysis Completed.\n")
            print("   Phase 2 Completed. Output saved.")

    except Exception as e:
        sys.stdout = original_stdout_phase2 if 'original_stdout_phase2' in locals() else sys.stdout
        # Log unexpected errors to the file
        with open(syntax_file_path, 'a') as f:
            f.write(f"\n[FATAL ERROR] {e}\n")
        print(f"   X Phase 2 Failed! See '{syntax_file_path}' for details.")
        print(">> Compilation Stopped.")
        return # STOP PROCESS

    # --- PHASE 3: SEMANTIC ANALYSIS ---
    print(">> Running Phase 3: Semantic Analysis...")
    
    # We need to capture the 'print' statements from SemanticAnalyzer to write them to the file
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_capture # Redirect stdout
    
    analyzer = SemanticAnalyzer()
    
    try:
        # This will print validation messages to output_capture
        analyzer.analyze(parse_tree) 
        
        # Restore stdout before writing to file
        sys.stdout = original_stdout 
        
        with open(semantic_file_path, 'w') as f:
            f.write("=== PHASE 3: SEMANTIC ANALYSIS (VERIFICATION & SYMBOL TABLE) ===\n\n")
            
            # Write the captured logs (User created, Grant successful, etc.)
            f.write("--- Semantic Checks Log ---\n")
            f.write(output_capture.getvalue())
            f.write("\nSemantic Analysis Successful. Query is valid.\n")
            
            # Dump Annotated Parse Tree (Required for Phase 3)
            f.write("\n--- ANNOTATED PARSE TREE (WITH SEMANTIC INFORMATION) ---\n")
            annotated_tree = analyzer.format_annotated_tree(parse_tree)
            f.write(annotated_tree)
            
            # Dump the Final Symbol Table (Required for Phase 3)
            f.write("\n\n--- FINAL SYMBOL TABLE (TABLES & COLUMNS) ---\n")
            if not analyzer.symbol_table:
                f.write("  (No tables defined)\n")
            for table_name, columns in analyzer.symbol_table.items():
                f.write(f"  Table: {table_name}\n")
                for col, dtype in columns.items():
                    f.write(f"    - Column: {col} (Type: {dtype})\n")
                f.write("\n")

            # Dump User Table (Extra Feature)
            f.write("--- FINAL USER CONFIGURATION ---\n")
            if not analyzer.user_table:
                f.write("  (No users defined)\n")
            for user, data in analyzer.user_table.items():
                f.write(f"  User: {user}\n")
                f.write(f"    - Password: {data['password']}\n")
                f.write(f"    - Privileges: {data['privileges']}\n")
            
            f.write("\n=== COMPILATION SUCCESSFUL ===\n")
            
        print("   Phase 3 Completed. Output saved.")
        print(f"\nSUCCESS: Full pipeline finished. Artifacts in '{output_dir}/'")

    except CompilerError as e:
        sys.stdout = original_stdout # Restore stdout immediately
        
        # Log what happened so far + the error
        with open(semantic_file_path, 'w') as f:
            f.write("=== PHASE 3: SEMANTIC ANALYSIS ===\n\n")
            f.write(output_capture.getvalue()) # Write partial success
            f.write(f"\n[FATAL ERROR] {e}\n")
            
        print(f"   X Phase 3 Failed! See '{semantic_file_path}' for details.")
        print(">> Compilation Stopped.")
        return # STOP PROCESS
    except Exception as e:
        sys.stdout = original_stdout
        print(f"\n[SYSTEM ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()