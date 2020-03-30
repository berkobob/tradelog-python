class AppError(AssertionError):
    def __init__(self, message, severity="ERROR"):
        self.message = message
        self.severity = severity