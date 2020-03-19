class Result_Iter:
    def __init__(self, result):
        self._result = result
        self._index = 0

    def __next__(self):
        if self._index > 2: raise StopIteration
        if self._index == 0: result = self._result.success
        if self._index == 1: result = self._result.message
        if self._index == 2: result = self._result.severity
        self._index += 1
        return result

        
class Result:
    def __init__(self, success: str, message=None, severity="SUCCESS"):
        self.success = success
        self.message = message
        self.severity = severity
        self.iter = [success, message, severity]
        self._index = 0

    def __repr__(self) -> str:
        return str(vars(self))

    def __iter__(self):
        return Result_Iter(self)