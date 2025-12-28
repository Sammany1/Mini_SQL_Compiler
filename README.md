Mini SQL Compiler
A lightweight compiler for SQL-like query languages implementing lexical, syntax, and semantic analysis phases. Built from scratch in Python without external parsing libraries.

Project Structure
text
Mini_SQL_Compiler/
├── compiler/
│   ├── lexer.py        # Phase 1: Tokenization
│   ├── parser.py       # Phase 2: AST Generation
│   ├── semantics.py    # Phase 3: Semantic Analysis
│   ├── ast_nodes.py    # AST Node Definitions
│   ├── tokens.py       # Token Types
│   └── errors.py       # Error Handling
├── main.py             # Compiler Pipeline
├── input.txt           # Sample Queries
└── outputs/            # Generated Analysis Reports
Installation & Usage
bash
# Clone repository
git clone <repo-url>
cd Mini_SQL_Compiler

# Run compiler
python main.py
The compiler reads from input.txt and generates timestamped outputs in the outputs/ directory.

License
Educational use - Compiler Design Course Project
