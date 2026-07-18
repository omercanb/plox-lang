from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from plox.types.lox_token import Token


class LoxError(ABC, Exception):
    def __init__(self, token: Optional["Token"], message: str):
        self.token = token
        self.message = message

    def __str__(self):
        if self.token is None:
            return f"Error: {self.message}"
        return f"Line {self.token.line} On '{self.token.lexeme}' Error: {self.message}"


class RuntimeError(LoxError):
    def __init__(self, token: Optional["Token"], message: str) -> None:
        self.token: Optional["Token"] = token
        self.message: str = message
        super().__init__(token, message)


class StaticError(LoxError):
    def __init__(self, token: Optional["Token"], message: str) -> None:
        self.token: Optional["Token"] = token
        self.message: str = message
        super().__init__(token, message)
