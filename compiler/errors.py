class CompilerError(Exception):
    """Custom exception for all compiler phases."""
    def __init__(self, message, line, column, phase):
        self.message = message
        self.line = line
        self.column = column
        self.phase = phase
        super().__init__(message)

    def __str__(self):
        return f"[{self.phase} Error] Line {self.line}, Col {self.column}: {self.message}"