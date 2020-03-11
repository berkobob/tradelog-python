class Result:
    def __init__(self, success: str, message=None, severity=None):
        self.success = success
        self.message = message
        self.severity = severity

    def __repr__(self) -> str:
        return str(vars(self))
