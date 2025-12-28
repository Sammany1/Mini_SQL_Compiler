# Mini SQL Compiler

A lightweight compiler for a SQL-like query language implementing **lexical**, **syntax**, and **semantic** analysis phases.  
Built from scratch in **Python**, without using external parsing libraries.

---

## Project Structure

```text
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
```
#Installation & Usage

# Clone repository
git clone repo-url

cd Mini_SQL_Compiler

# Run compiler
python main.py
