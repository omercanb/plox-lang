from typing import TYPE_CHECKING, Any, Dict, Optional

from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self.values: Dict[str, Any] = {}
        self.enclosing: Optional[Environment] = enclosing

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get_at(self, name: Token, distance: int) -> Any:
        if distance == 0:
            # Static analysis should have told that this variable is undefined
            if name.lexeme not in self.values:
                raise RuntimeError(name, "Name not defined")
            assert name.lexeme in self.values
            return self.values[name.lexeme]
        return self.enclosing.get_at(name, distance - 1)

    def assign_at(self, name: Token, value: Any, distance: int):
        if distance == 0:
            self.values[name.lexeme] = value
        else:
            self.enclosing.assign_at(name, value, distance - 1)

    # def get(self, name: "Token") -> Any:
    #     if name.lexeme in self.values:
    #         return self.values[name.lexeme]
    #     if self.enclosing is not None:
    #         return self.enclosing.get(name)
    #
    #     raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    #
    # def assign(self, name: "Token", value: Any) -> None:
    #     if name.lexeme in self.values:
    #         self.values[name.lexeme] = value
    #         return
    #     if self.enclosing is not None:
    #         self.enclosing.assign(name, value)
    #         return
    #
    #     raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
