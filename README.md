# Mini SQL Compiler

A complete three-phase compiler for a SQL-like query language, implementing **lexical analysis**, **syntax analysis**, and **semantic analysis**. Built from scratch in **Python** without using external parsing libraries or code generators.

---

## 📋 Project Overview

This compiler processes SQL-like queries through three distinct phases:

1. **Phase 1: Lexical Analysis (Lexer)** - Tokenizes source code
2. **Phase 2: Syntax Analysis (Parser)** - Validates grammar and builds parse tree
3. **Phase 3: Semantic Analysis** - Checks semantic correctness and type compatibility

---

## 🏗️ Project Structure

```
Mini_SQL_Compiler/
│
├── compiler/                    # Core compiler modules
│   ├── __init__.py
│   ├── lexer.py                # Phase 1: Lexical Analyzer
│   ├── parser.py               # Phase 2: Syntax Analyzer (Recursive Descent)
│   ├── semantics.py            # Phase 3: Semantic Analyzer
│   ├── ast_nodes.py            # AST Node Class Definitions
│   ├── tokens.py               # Token Type Enumeration
│   └── errors.py               # Custom Error Handling
│
├── main.py                     # Main compiler pipeline
├── input.txt                   # Input SQL queries
├── outputs/                    # Generated output files (created at runtime)
│   └── Run_YYYY-MM-DD_HH-MM-SS/
│       ├── 1_Lexical_Analysis.txt
│       ├── 2_Syntax_Analysis.txt
│       └── 3_Semantic_Analysis.txt
│
└── README.md                   # This file
```

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.7 or higher

### Running the Compiler

1. **Navigate to the project directory:**
   ```bash
   cd Mini_SQL_Compiler
   ```

2. **Prepare your SQL input:**
   - Edit `input.txt` with your SQL queries
   - Each statement should end with a semicolon (`;`)
   - Do not include line numbers or prefixes

3. **Run the compiler:**
   ```bash
   python main.py
   ```

4. **Check the output:**
   - Output files are generated in `outputs/Run_YYYY-MM-DD_HH-MM-SS/`
   - Three files are created:
     - `1_Lexical_Analysis.txt` - Token stream
     - `2_Syntax_Analysis.txt` - Parse tree and syntax errors
     - `3_Semantic_Analysis.txt` - Semantic checks, symbol table, and annotated parse tree

---

## 📝 Supported SQL Syntax

### Statements Supported

#### 1. CREATE TABLE
```sql
CREATE TABLE table_name (col1 TYPE1, col2 TYPE2, ...);
```
- Types: `INT`, `FLOAT`, `TEXT`
- Example: `CREATE TABLE students (id INT, name TEXT, age INT);`

#### 2. INSERT
```sql
INSERT INTO table_name VALUES (val1, val2, ...);
```
- Example: `INSERT INTO students VALUES (101, 'Alice', 20);`

#### 3. SELECT
```sql
SELECT col1, col2, ... FROM table_name [WHERE condition];
SELECT * FROM table_name [WHERE condition];
```
- Example: `SELECT * FROM students WHERE id = 101 AND age > 18;`

#### 4. UPDATE
```sql
UPDATE table_name SET col1 = val1, col2 = val2 [WHERE condition];
```
- Example: `UPDATE students SET name = 'Bob' WHERE id = 101;`

#### 5. DELETE
```sql
DELETE FROM table_name [WHERE condition];
```
- Example: `DELETE FROM students WHERE id = 101;`

#### 6. CREATE USER (Extended Feature)
```sql
CREATE USER username IDENTIFIED BY 'password';
```

#### 7. GRANT (Extended Feature)
```sql
GRANT privilege ON table_name TO username;
```

### WHERE Clause Conditions

Supports compound conditions with operators:
- **Comparison operators**: `=`, `!=`, `<>`, `<`, `>`, `<=`, `>=`
- **Logical operators**: `AND`, `OR`, `NOT`
- **Examples**:
  - `WHERE id = 1`
  - `WHERE id = 1 AND name = 'Alice'`
  - `WHERE age > 18 OR status = 'active'`
  - `WHERE NOT deleted = 1`

### Comments
- Single-line: `-- comment text`
- Multi-line: `## comment text ##`

---

## 🔍 Compiler Phases

### Phase 1: Lexical Analysis
- **Purpose**: Tokenize source code into tokens
- **Output**: Stream of tokens (keywords, identifiers, literals, operators, delimiters)
- **Features**:
  - Case-sensitive keyword recognition
  - Number literal handling (INT and FLOAT)
  - String literal handling
  - Comment handling
  - Immediate error detection for illegal characters

### Phase 2: Syntax Analysis
- **Technique**: Recursive Descent Parsing
- **Purpose**: Validate grammar and build Abstract Syntax Tree (AST)
- **Output**: Parse tree (AST nodes)
- **Features**:
  - Grammar validation
  - Parse tree generation
  - Error recovery (panic mode)
  - Multiple error detection in one run

### Phase 3: Semantic Analysis
- **Purpose**: Verify semantic correctness
- **Output**: Annotated parse tree, symbol table dump
- **Checks**:
  - Table and column existence
  - Type compatibility (INSERT, UPDATE, WHERE)
  - Redeclaration prevention
  - Compound condition validation
- **Features**:
  - Symbol table management
  - Type checking
  - Semantic annotations
  - Comprehensive error reporting

---

## 📊 Output Format

### Phase 1 Output
- Token stream with line/column numbers
- Token type and lexeme for each token

### Phase 2 Output
- Parse tree structure
- Syntax errors (if any) with recovery information

### Phase 3 Output
- Semantic check log
- Annotated parse tree with:
  - Data types for all identifiers and literals
  - Symbol table references
  - Type compatibility information
- Final symbol table dump

---

## ⚠️ Error Handling

The compiler provides comprehensive error reporting:

- **Lexical Errors**: Illegal characters detected immediately
- **Syntax Errors**: Reported with line/column numbers, error recovery continues parsing
- **Semantic Errors**: Type mismatches, undefined tables/columns, etc.

All errors include:
- Error type (Lexical/Syntax/Semantic)
- Line number
- Column number
- Descriptive error message

---

## 🛠️ Implementation Details

### Key Design Decisions

1. **Recursive Descent Parsing**: Direct mapping from grammar rules to code
2. **Symbol Table**: Dictionary-based structure for efficient lookups
3. **AST Nodes**: Object-oriented representation of parsed statements
4. **Error Recovery**: Panic mode for syntax errors to find multiple errors per run
5. **Type System**: Three types (INT, FLOAT, TEXT) with strict compatibility checking

### Built From Scratch

- ✅ No external parsing libraries (no Yacc, Bison, Antlr)
- ✅ Custom tokenizer implementation
- ✅ Custom recursive descent parser
- ✅ Custom semantic analyzer with symbol table
- ✅ Custom error handling system

---

## 📚 Example Usage

### Input File (`input.txt`)
```sql
CREATE TABLE students (id INT, name TEXT, age INT);
INSERT INTO students VALUES (101, 'Alice', 20);
SELECT * FROM students WHERE id = 101;
UPDATE students SET name = 'Bob' WHERE age > 18;
DELETE FROM students WHERE id = 101 AND age = 20;
```

### Running the Compiler
```bash
python main.py
```

### Expected Output
- ✅ All three phases complete successfully
- ✅ Token stream generated
- ✅ Parse tree built
- ✅ Semantic analysis passed
- ✅ Symbol table dumped
- ✅ Annotated parse tree generated

---

## 📄 License

This project is developed as an academic assignment for CSCI415 - Compiler Design.

---

## 👥 Authors

Developed as part of the Compiler Design course project.

---

## 📞 Support

For issues or questions regarding the compiler implementation, please refer to the project documentation or contact the development team.
