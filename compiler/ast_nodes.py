class SQLNode:
    """Base class for all AST nodes."""
    pass

class Statement(SQLNode):
    pass

class CreateTable(Statement):
    def __init__(self, table_name, columns, line):
        self.table_name = table_name
        self.columns = columns  # List of (name, type)
        self.line = line

class Insert(Statement):
    def __init__(self, table_name, values, line):
        self.table_name = table_name
        self.values = values    # List of values
        self.line = line

class Select(Statement):
    def __init__(self, table_name, columns, condition, line):
        self.table_name = table_name
        self.columns = columns  # List of names or '*'
        self.condition = condition # Optional tuple (col, op, val)
        self.line = line

class CreateUser(Statement):
    def __init__(self, username, password, line):
        self.username = username
        self.password = password
        self.line = line

    def __repr__(self):
        return f"CreateUser(user='{self.username}', password='***')"

class Grant(Statement):
    def __init__(self, privilege, table_name, user_name, line):
        self.privilege = privilege # e.g., 'SELECT', 'INSERT'
        self.table_name = table_name
        self.user_name = user_name
        self.line = line

    def __repr__(self):
        return f"Grant(privilege='{self.privilege}', table='{self.table_name}', user='{self.user_name}')"

class Update(Statement):
    def __init__(self, table_name, assignments, condition, line):
        self.table_name = table_name
        self.assignments = assignments  # List of (column, value) tuples
        self.condition = condition  # Optional condition tuple or compound condition
        self.line = line

    def __repr__(self):
        cond_str = str(self.condition) if self.condition else "None"
        return f"Update(table='{self.table_name}', assignments={self.assignments}, condition={cond_str})"

class Delete(Statement):
    def __init__(self, table_name, condition, line):
        self.table_name = table_name
        self.condition = condition  # Optional condition tuple or compound condition
        self.line = line

    def __repr__(self):
        cond_str = str(self.condition) if self.condition else "None"
        return f"Delete(table='{self.table_name}', condition={cond_str})"