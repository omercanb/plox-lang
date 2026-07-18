from typing import TYPE_CHECKING, Any, List

from plox.native_functions.native_classes import NativeClass
from plox.types.lox_callable import LoxCallable, LoxInstance
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class NativeArrayMethod(LoxCallable):
    """Base class for array methods"""

    def __init__(self, array: "LoxArray"):
        self.array = array


class AppendMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        self.array.elements.append(arguments[0])
        return None

    def __str__(self):
        return "<array method append>"


class PopMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot pop from empty array.")
        return self.array.elements.pop()

    def __str__(self):
        return "<array method pop>"


class LengthMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return len(self.array.elements)

    def __str__(self):
        return "<array method length>"


class ClearMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        self.array.elements.clear()
        return None

    def __str__(self):
        return "<array method clear>"


class RemoveMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        try:
            self.array.elements.remove(arguments[0])
            return None
        except ValueError:
            raise RuntimeError(None, "Element not found in array.")

    def __str__(self):
        return "<array method remove>"


class InsertMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 2

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        index, value = arguments
        idx = self.array._validate_index_type(index)
        self.array._check_insert_bounds(idx)
        self.array.elements.insert(idx, value)
        return None

    def __str__(self):
        return "<array method insert>"


class IndexMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        value = arguments[0]
        try:
            return self.array.elements.index(value)
        except ValueError:
            return -1

    def __str__(self):
        return "<array method index>"


class ReverseMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        self.array.elements.reverse()
        return None

    def __str__(self):
        return "<array method reverse>"


class ContainsMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return arguments[0] in self.array.elements

    def __str__(self):
        return "<array method contains>"


class FirstMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot get first element of empty array.")
        return self.array.elements[0]

    def __str__(self):
        return "<array method first>"


class LastMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot get last element of empty array.")
        return self.array.elements[-1]

    def __str__(self):
        return "<array method last>"


class RemoveAtMethod(NativeArrayMethod):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        index = arguments[0]
        idx = self.array._validate_index_type(index)
        self.array._check_read_bounds(idx)
        return self.array.elements.pop(idx)

    def __str__(self):
        return "<array method remove_at>"


class NativeArray(NativeClass):
    def __init__(self):
        from plox.types.lox_token import Token
        from plox.types.token_type import TokenType

        name = Token(TokenType.IDENTIFIER, "array", None, 0)
        super().__init__(name, {}, None)

    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray(self)

    def __str__(self):
        return "<native fn array>"


class LoxArray(LoxInstance):
    def __init__(self, cls: NativeArray):
        self.cls = cls
        self.elements: List[Any] = []

    def is_truthy(self) -> bool:
        return len(self.elements) > 0

    def _validate_index_type(self, index: Any) -> int:
        """Convert index to int, raise if not a number."""
        if not isinstance(index, (int, float)):
            raise RuntimeError(None, "Array index must be a number.")
        return int(index)

    def _check_read_bounds(self, index: int) -> None:
        """Check if index is valid for reading (0 <= index < len)."""
        if index < 0 or index >= len(self.elements):
            raise RuntimeError(None, f"Index {index} out of bounds.")

    def _check_insert_bounds(self, index: int) -> None:
        """Check if index is valid for inserting (0 <= index <= len)."""
        if index < 0 or index > len(self.elements):
            raise RuntimeError(None, f"Index {index} out of bounds.")

    def get(self, name: Token) -> Any:
        methods = {
            "append": AppendMethod,
            "pop": PopMethod,
            "length": LengthMethod,
            "clear": ClearMethod,
            "remove": RemoveMethod,
            "insert": InsertMethod,
            "index": IndexMethod,
            "reverse": ReverseMethod,
            "contains": ContainsMethod,
            "first": FirstMethod,
            "last": LastMethod,
            "remove_at": RemoveAtMethod,
        }
        if name.lexeme in methods:
            return methods[name.lexeme](self)
        raise RuntimeError(name, f"Array has no method '{name.lexeme}'.")

    def get_index(self, token: Token, index: Any) -> Any:
        idx = self._validate_index_type(index)
        self._check_read_bounds(idx)
        return self.elements[idx]

    def set_index(self, token: Token, index: Any, value: Any) -> Any:
        idx = self._validate_index_type(index)
        self._check_read_bounds(idx)
        self.elements[idx] = value
        return value

    def __str__(self):
        return f"[{', '.join(str(e) for e in self.elements)}]"

    def __repr__(self):
        return self.__str__()
