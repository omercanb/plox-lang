from typing import TYPE_CHECKING, Any, List

from plox.builtin_functions.builtin_classes import BuiltinClass
from plox.types.lox_callable import LoxCallable, LoxInstance
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinStringMethod(LoxCallable):
    """Base class for string methods"""

    def __init__(self, string: "LoxString"):
        self.string = string


class LengthMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return len(self.string.value)

    def __str__(self):
        return "<string method length>"


class UpperMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxString":
        return LoxString(self.string.value.upper())

    def __str__(self):
        return "<string method upper>"


class LowerMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxString":
        return LoxString(self.string.value.lower())

    def __str__(self):
        return "<string method lower>"


class StripMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxString":
        return LoxString(self.string.value.strip())

    def __str__(self):
        return "<string method strip>"


class SplitMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        from plox.builtin_functions.builtin_array import LoxArray

        parts = self.string.value.split()
        return LoxArray([LoxString(p) for p in parts])

    def __str__(self):
        return "<string method split>"


class ReplaceMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 2

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxString":
        old, new = arguments
        if not isinstance(old, LoxString):
            old = LoxString(str(old))
        if not isinstance(new, LoxString):
            new = LoxString(str(new))
        return LoxString(self.string.value.replace(old.value, new.value))

    def __str__(self):
        return "<string method replace>"


class StartsWithMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> bool:
        prefix = arguments[0]
        if isinstance(prefix, LoxString):
            prefix = prefix.value
        else:
            prefix = str(prefix)
        return self.string.value.startswith(prefix)

    def __str__(self):
        return "<string method startswith>"


class EndsWithMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> bool:
        suffix = arguments[0]
        if isinstance(suffix, LoxString):
            suffix = suffix.value
        else:
            suffix = str(suffix)
        return self.string.value.endswith(suffix)

    def __str__(self):
        return "<string method endswith>"


class FindMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> int:
        substring = arguments[0]
        if isinstance(substring, LoxString):
            substring = substring.value
        else:
            substring = str(substring)
        idx = self.string.value.find(substring)
        return idx if idx != -1 else -1

    def __str__(self):
        return "<string method find>"


class ContainsMethod(BuiltinStringMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> bool:
        substring = arguments[0]
        if isinstance(substring, LoxString):
            substring = substring.value
        else:
            substring = str(substring)
        return substring in self.string.value

    def __str__(self):
        return "<string method contains>"


class BuiltinString(BuiltinClass):
    def __init__(self):
        name = Token(TokenType.IDENTIFIER, "string", None, 0)
        super().__init__(name, {}, None)

    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxString":
        if len(arguments) > 0:
            value = arguments[0]
            if isinstance(value, LoxString):
                return value
            return LoxString(str(value) if value is not None else "nil")
        return LoxString("")

    def __str__(self):
        return "<builtin string>"


class LoxString(LoxInstance):
    def __init__(self, value: str = ""):
        self.value = str(value)
        super().__init__(BuiltinString())

    def is_truthy(self) -> bool:
        return len(self.value) > 0

    def _validate_index_type(self, index: Any) -> int:
        """Convert index to int, raise if not a number."""
        if not isinstance(index, (int, float)):
            raise RuntimeError(None, "String index must be a number.")
        return int(index)

    def _check_read_bounds(self, index: int) -> None:
        """Check if index is valid for reading (0 <= index < len)."""
        if index < 0 or index >= len(self.value):
            raise RuntimeError(None, f"Index {index} out of bounds.")

    def get_index(self, token: Token, index: Any) -> str:
        idx = self._validate_index_type(index)
        self._check_read_bounds(idx)
        return self.value[idx]

    def set_index(self, token: Token, index: Any, value: Any) -> Any:
        raise RuntimeError(None, "Strings are immutable.")

    def get(self, name: Token) -> Any:
        methods = {
            "length": LengthMethod(self),
            "upper": UpperMethod(self),
            "lower": LowerMethod(self),
            "strip": StripMethod(self),
            "split": SplitMethod(self),
            "replace": ReplaceMethod(self),
            "startswith": StartsWithMethod(self),
            "endswith": EndsWithMethod(self),
            "find": FindMethod(self),
            "contains": ContainsMethod(self),
        }
        if name.lexeme in methods:
            return methods[name.lexeme]
        raise RuntimeError(name, f"String has no method '{name.lexeme}'.")

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'

    def __add__(self, other):
        return LoxString(self.value + other.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, LoxString):
            return self.value == other.value
        return self.value == other
