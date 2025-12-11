# ========================================
# test_valid.txt
# Tests all statement types with valid syntax
# ========================================

CREATE TABLE students (id INT, name TEXT, grade FLOAT);
INSERT INTO students VALUES (1, 'Ali', 85.5);
INSERT INTO students VALUES (2, 'Sara', 92.0);
SELECT name FROM students WHERE id = 1;
SELECT * FROM students WHERE grade > 80.0;
UPDATE students SET grade = 95.0 WHERE name = 'Ali';
DELETE FROM students WHERE id = 2;

# ========================================
# test_conditions.txt
# Tests complex WHERE conditions
# ========================================

SELECT name FROM students WHERE id = 1 AND grade > 80.0;
SELECT name FROM students WHERE id = 1 OR id = 2;
SELECT name FROM students WHERE NOT grade < 60.0;
SELECT name FROM students WHERE (id = 1 OR id = 2) AND grade > 85.0;
SELECT name FROM students WHERE id = 1 AND (grade > 80.0 OR grade < 70.0);
DELETE FROM students WHERE NOT (id = 1 OR id = 2);

# ========================================
# test_errors.txt
# Tests various syntax errors
# ========================================

-- Missing semicolon
SELECT name FROM students

-- Missing FROM keyword
SELECT name students WHERE id = 1;

-- Missing WHERE condition
SELECT name FROM students WHERE;

-- Missing closing parenthesis
CREATE TABLE test (id INT, name TEXT;

-- Invalid comparison operator
SELECT name FROM students WHERE id # 1;

-- Missing table name
INSERT INTO VALUES (1, 'test');

-- Missing equal sign in UPDATE
UPDATE students SET name 'newname' WHERE id = 1;

# ========================================
# test_mixed.txt
# Mix of valid and invalid statements (tests error recovery)
# ========================================

CREATE TABLE products (id INT, name TEXT, price FLOAT);
INSERT INTO products VALUES (1, 'Laptop', 999.99);

-- This line has an error (missing FROM)
SELECT name products WHERE price > 500.0;

-- Parser should recover and continue
INSERT INTO products VALUES (2, 'Mouse', 25.50);
SELECT * FROM products WHERE id = 1 OR id = 2;

-- Another error (missing right paren)
UPDATE products SET price = 1099.99 WHERE (id = 1;

-- Should still parse this correctly
DELETE FROM products WHERE price < 30.0;
