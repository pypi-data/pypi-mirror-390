from typing import List


class PargsException(Exception):
    pass


class ParserTypeError(PargsException):
    def __init__(self, expected_type: object, error: Exception):
        super().__init__()
        self.expected_type = expected_type
        self.e = error

    def __str__(self):
        return f"Expected type {self.expected_type!r}, got error {self.e!r}"


class PargsUnkownArgument(PargsException):
    def __init__(self, items: List[str]) -> None:
        self.items = items

    def __str__(self) -> str:
        return f"Unkown arguments {', '.join(self.items)}"


class PargsMissingArgument(PargsException):
    def __init__(self, items: List[str]) -> None:
        self.items = items

    def __str__(self) -> str:
        return f"Missing arguments {', '.join(self.items)}"
