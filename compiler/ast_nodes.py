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