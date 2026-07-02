from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plox.types.lox_token import Token

class StaticError(Exception):
    def __init__(self, token: "Token", message: str) -> None:
        self.token: "Token" = token
        self.message: str = message
        super().__init__(message)
