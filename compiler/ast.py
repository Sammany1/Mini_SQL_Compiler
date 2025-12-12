"""
Abstract Syntax Tree (Parse Tree) nodes for the SQL-like language.
Each node represents a construct in the grammar.
"""

class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self):
        self.node_type = self.__class__.__name__
    
    def to_tree_string(self):
        """Generate tree-style ASCII representation."""
        lines = self._build_tree_lines()
        return '\n'.join(lines)
    
    def _build_tree_lines(self):
        """Build tree lines recursively. Returns list of lines."""
        raise NotImplementedError("Subclasses must implement _build_tree_lines")
    
    def _to_string(self, indent=0):
        """Legacy method - now uses tree format."""
        return self.to_tree_string()
    
    @staticmethod
    def _render_tree(label, children_data, width=80):
        """
        Render a tree node with children in the exact format shown in the example.
        children_data: list of tuples (label, subtree_lines) or just strings for leaves
        Returns: list of lines
        """
        lines = []
        
        # Center the root label
        root_line = " " * 32 + label
        lines.append(root_line)
        
        if not children_data:
            return lines
        
        # Process children - convert to (label, subtree_lines or None) format
        processed_children = []
        for child in children_data:
            if isinstance(child, tuple) and len(child) == 2:
                processed_children.append(child)
            elif isinstance(child, list) and len(child) == 2:
                processed_children.append((child[0], child[1]))
            else:
                processed_children.append((str(child), None))
        
        if not processed_children:
            return lines
        
        # Calculate positions for children
        child_labels = [label for label, _ in processed_children]
        child_widths = [len(label) for label in child_labels]
        
        # Calculate total width and starting position
        spacing = 3
        total_width = sum(child_widths) + spacing * (len(child_widths) - 1)
        root_center = 32 + len(label) // 2
        start_pos = root_center - total_width // 2
        
        # Calculate center positions for each child
        child_positions = []
        current_pos = start_pos
        for width in child_widths:
            center = current_pos + width // 2
            child_positions.append((current_pos, center, current_pos + width))
            current_pos += width + spacing
        
        # Build branch line (horizontal line with ┴ at child centers)
        max_len = max(root_center + total_width + 10, child_positions[-1][2] + 5)
        branch_line = [" "] * max_len
        
        if len(child_positions) > 1:
            first_center = child_positions[0][1]
            last_center = child_positions[-1][1]
            # Draw horizontal line connecting all children
            for i in range(first_center, last_center + 1):
                if 0 <= i < len(branch_line):
                    branch_line[i] = "-"
            # Place + at root center
            if 0 <= root_center < len(branch_line):
                branch_line[root_center] = "+"
            # Place + at each child center (overwrites the -)
            for _, center, _ in child_positions:
                if 0 <= center < len(branch_line):
                    branch_line[center] = "+"
        else:
            # Single child - draw line from root to child
            child_center = child_positions[0][1]
            start_line = min(root_center, child_center)
            end_line = max(root_center, child_center)
            for i in range(start_line, end_line + 1):
                if 0 <= i < len(branch_line):
                    branch_line[i] = "-"
            branch_line[root_center] = "+"
            if 0 <= child_center < len(branch_line):
                branch_line[child_center] = "+"
        
        branch_str = "".join(branch_line).rstrip()
        lines.append(branch_str)
        
        # Vertical bars line
        bars_line = [" "] * len(branch_str)
        for _, center, _ in child_positions:
            if 0 <= center < len(bars_line):
                bars_line[center] = "|"
        lines.append("".join(bars_line))
        
        # Child labels line
        labels_line = [" "] * len(branch_str)
        for (start, center, end), label in zip(child_positions, child_labels):
            label_start = center - len(label) // 2
            for i, char in enumerate(label):
                pos = label_start + i
                if 0 <= pos < len(labels_line):
                    labels_line[pos] = char
        lines.append("".join(labels_line))
        
        # Render nested subtrees
        has_nested = any(subtree is not None for _, subtree in processed_children)
        if has_nested:
            # Find max height of nested subtrees
            nested_heights = []
            nested_subtrees = []
            for _, subtree in processed_children:
                if subtree is not None and isinstance(subtree, list):
                    nested_heights.append(len(subtree))
                    nested_subtrees.append(subtree)
                else:
                    nested_heights.append(0)
                    nested_subtrees.append(None)
            
            max_height = max(nested_heights) if nested_heights else 0
            
            # Render each level of nested subtrees
            # Need to make the line wide enough for all subtrees
            max_line_width = len(branch_str)
            for subtree in nested_subtrees:
                if subtree:
                    for line in subtree:
                        # Strip leading whitespace and measure actual content width
                        stripped = line.lstrip()
                        if stripped:
                            max_line_width = max(max_line_width, len(stripped) + 50)
            
            for line_idx in range(max_height):
                combined_line = [" "] * max_line_width
                
                for (start, center, end), (label, subtree) in zip(child_positions, processed_children):
                    if subtree is not None and isinstance(subtree, list) and line_idx < len(subtree):
                        subtree_line = str(subtree[line_idx])
                        # Strip leading whitespace from nested tree lines
                        stripped_line = subtree_line.lstrip()
                        if stripped_line:
                            # Place vertical bar at child center (but extend line if needed)
                            if center >= len(combined_line):
                                combined_line.extend([" "] * (center - len(combined_line) + 1))
                            if 0 <= center < len(combined_line):
                                combined_line[center] = "|"
                            
                            # Center the stripped subtree line under the parent label
                            subtree_width = len(stripped_line)
                            subtree_start = center - subtree_width // 2
                            
                            # Extend line if needed
                            needed_len = subtree_start + subtree_width
                            if needed_len > len(combined_line):
                                combined_line.extend([" "] * (needed_len - len(combined_line)))
                            
                            # Place subtree line content centered under parent
                            for i, char in enumerate(stripped_line):
                                pos = subtree_start + i
                                if 0 <= pos < len(combined_line):
                                    # Only overwrite spaces, preserve bars
                                    if combined_line[pos] == " ":
                                        combined_line[pos] = char
                
                lines.append("".join(combined_line).rstrip())
        
        return lines

# Statement nodes
class Statement(ASTNode):
    """Base class for all SQL statements."""
    pass

class CreateTableStatement(Statement):
    """CREATE TABLE statement."""
    def __init__(self, table_name, columns):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
    
    def _build_tree_lines(self):
        children = ["CREATE", "TABLE", self.table_name, "(", "ColumnDefList"]
        
        # Add column definitions
        for col_name, col_type in self.columns:
            children.append(col_name)
            if col_type:
                children.append(col_type)
            else:
                children.append("ERROR")
        
        children.extend([")", ";"])
        return self._render_tree("CreateStmt", children)

class InsertStatement(Statement):
    """INSERT INTO statement."""
    def __init__(self, table_name, values):
        super().__init__()
        self.table_name = table_name
        self.values = values
    
    def _build_tree_lines(self):
        children = ["INSERT", "INTO", self.table_name, "VALUES", "(", "ValueList"]
        
        # Add values
        for val in self.values:
            if isinstance(val, Value):
                children.append(val.value)
            else:
                children.append("ERROR")
        
        children.extend([")", ";"])
        return self._render_tree("InsertStmt", children)

class SelectStatement(Statement):
    """SELECT statement."""
    def __init__(self, select_list, table_name, where_clause=None):
        super().__init__()
        self.select_list = select_list
        self.table_name = table_name
        self.where_clause = where_clause
    
    def _build_tree_lines(self):
        children = ["SELECT", "SelectList"]
        
        # Add select list items
        if self.select_list == ['*']:
            children.append("*")
        else:
            for item in self.select_list:
                children.append(item)
        
        children.extend(["FROM", self.table_name])
        
        # Add WHERE clause
        if self.where_clause:
            where_lines = self.where_clause._build_tree_lines()
            children.append(("Where", where_lines))
        else:
            children.append("WhereOpt")
        
        children.append(";")
        return self._render_tree("SelectStmt", children)

class UpdateStatement(Statement):
    """UPDATE statement."""
    def __init__(self, table_name, assignments, where_clause=None):
        super().__init__()
        self.table_name = table_name
        self.assignments = assignments
        self.where_clause = where_clause
    
    def _build_tree_lines(self):
        children = ["UPDATE", self.table_name, "SET", "AssignList"]
        
        # Add assignments
        for col_name, val in self.assignments:
            children.append(col_name)
            children.append("=")
            if isinstance(val, Value):
                children.append(val.value)
            else:
                children.append("ERROR")
        
        # Add WHERE clause
        if self.where_clause:
            where_lines = self.where_clause._build_tree_lines()
            children.append(("Where", where_lines))
        else:
            children.append("WhereOpt")
        
        children.append(";")
        return self._render_tree("UpdateStmt", children)

class DeleteStatement(Statement):
    """DELETE statement."""
    def __init__(self, table_name, where_clause=None):
        super().__init__()
        self.table_name = table_name
        self.where_clause = where_clause
    
    def _build_tree_lines(self):
        children = ["DELETE", "FROM", self.table_name]
        
        # Add WHERE clause
        if self.where_clause:
            where_lines = self.where_clause._build_tree_lines()
            children.append(("Where", where_lines))
        else:
            children.append("WhereOpt")
        
        children.append(";")
        return self._render_tree("DeleteStmt", children)

# Expression nodes
class Expression(ASTNode):
    """Base class for expressions."""
    pass

class Value(Expression):
    """A literal value (number, string, or identifier)."""
    def __init__(self, value, value_type):
        super().__init__()
        self.value = value
        self.value_type = value_type
    
    def _build_tree_lines(self):
        return [str(self.value)]

class Condition(Expression):
    """A condition (comparison or boolean expression)."""
    def __init__(self, left, operator, right=None):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    
    def _build_tree_lines(self):
        op_map = {'EQUAL': '=', 'NOT_EQUAL': '!=', 'LESS_THAN': '<', 
                  'LESS_EQUAL': '<=', 'GREATER_THAN': '>', 'GREATER_EQUAL': '>='}
        op_symbol = op_map.get(self.operator.name, self.operator.name)
        
        children = []
        
        # Left operand
        if isinstance(self.left, Value):
            children.append(self.left.value)
        else:
            left_lines = self.left._build_tree_lines()
            children.append(("Expr", left_lines))
        
        # Operator
        children.append(op_symbol)
        
        # Right operand
        if self.right:
            if isinstance(self.right, Value):
                children.append(self.right.value)
            else:
                right_lines = self.right._build_tree_lines()
                children.append(("Expr", right_lines))
        else:
            children.append("ERROR")
        
        return self._render_tree("Comparison", children)

class BooleanExpression(Expression):
    """A boolean expression (AND, OR, NOT)."""
    def __init__(self, left, operator, right=None):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    
    def _build_tree_lines(self):
        op_name = self.operator.name
        
        if op_name == "NOT":
            label = "NotExpr"
            left_lines = self.left._build_tree_lines()
            children = [("Expr", left_lines)]
        elif op_name == "AND":
            label = "AndExpr"
            left_lines = self.left._build_tree_lines()
            right_lines = self.right._build_tree_lines()
            children = [("Expr", left_lines), ("Expr", right_lines)]
        else:  # OR
            label = "OrExpr"
            left_lines = self.left._build_tree_lines()
            right_lines = self.right._build_tree_lines()
            children = [("Expr", left_lines), ("Expr", right_lines)]
        
        return self._render_tree(label, children)
