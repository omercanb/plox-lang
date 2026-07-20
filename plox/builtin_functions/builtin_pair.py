from typing import TYPE_CHECKING, Any, List

from plox.builtin_functions.builtin_classes import BuiltinClass
from plox.types.lox_callable import (
    LoxBindableMethod,
    LoxCallable,
    LoxFunction,
    LoxInstance,
)
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinPairMethod(LoxBindableMethod):
    """Base class for pair methods"""

    pair: "LoxPair"

    def bind(self, instance: "LoxPair"):
        method = type(self)()
        method.pair = instance
        return method


class CopyMethod(BuiltinPairMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxPair":
        return LoxPair(self.pair.first, self.pair.second)

    def __str__(self):
        return "<pair method copy>"


class BuiltinPair(BuiltinClass):
    def __init__(self):
        name = Token(TokenType.IDENTIFIER, "pair", None, 0)
        methods: dict[str, LoxBindableMethod] = {
            "copy": CopyMethod(),
        }
        super().__init__(name, methods, None)

    def arity(self):
        return 2

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxPair":
        first, second = arguments
        return LoxPair(first, second)

    def __str__(self):
        return "<builtin fn pair>"


class LoxPair(LoxInstance):
    def __init__(self, first: Any, second: Any):
        super().__init__(BuiltinPair())
        self.fields["first"] = first
        self.fields["second"] = second

    @property
    def first(self) -> Any:
        return self.fields["first"]

    @property
    def second(self) -> Any:
        return self.fields["second"]

    def __str__(self):
        return f"({self.first}, {self.second})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            isinstance(other, LoxPair)
            and self.first == other.first
            and self.second == other.second
        )
