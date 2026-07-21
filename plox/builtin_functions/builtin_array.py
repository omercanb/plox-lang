from typing import TYPE_CHECKING, Any, List

from plox.builtin_functions.builtin_classes import BuiltinClass
from plox.types.lox_callable import LoxBindableMethod, LoxCallable, LoxInstance
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinArrayMethod(LoxBindableMethod):
    """Base class for array methods"""

    array: "LoxArray"

    def bind(self, instance: "LoxArray"):
        method = type(self)()
        method.array = instance
        return method


class AppendMethod(BuiltinArrayMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.array.elements.append(arguments[0])
        return None

    def __str__(self):
        return "<array method append>"


class PopMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot pop from empty array.")
        return self.array.elements.pop()

    def __str__(self):
        return "<array method pop>"


class LengthMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return len(self.array.elements)

    def __str__(self):
        return "<array method length>"


class ClearMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.array.elements.clear()
        return None

    def __str__(self):
        return "<array method clear>"


class RemoveMethod(BuiltinArrayMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        try:
            self.array.elements.remove(arguments[0])
            return True
        except ValueError:
            return False

    def __str__(self):
        return "<array method remove>"


class InsertMethod(BuiltinArrayMethod):
    def arity(self):
        return 2

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        index, value = arguments
        idx = self.array._validate_index_type(index)
        self.array._check_insert_bounds(idx)
        self.array.elements.insert(idx, value)
        return None

    def __str__(self):
        return "<array method insert>"


class IndexMethod(BuiltinArrayMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        value = arguments[0]
        try:
            return self.array.elements.index(value)
        except ValueError:
            return -1

    def __str__(self):
        return "<array method index>"


class ReverseMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.array.elements.reverse()
        return None

    def __str__(self):
        return "<array method reverse>"


class ContainsMethod(BuiltinArrayMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return arguments[0] in self.array.elements

    def __str__(self):
        return "<array method contains>"


class FirstMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot get first element of empty array.")
        return self.array.elements[0]

    def __str__(self):
        return "<array method first>"


class LastMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        if len(self.array.elements) == 0:
            raise RuntimeError(None, "Cannot get last element of empty array.")
        return self.array.elements[-1]

    def __str__(self):
        return "<array method last>"


class RemoveAtMethod(BuiltinArrayMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        index = arguments[0]
        idx = self.array._validate_index_type(index)
        self.array._check_read_bounds(idx)
        return self.array.elements.pop(idx)

    def __str__(self):
        return "<array method remove_at>"


class SliceMethod(BuiltinArrayMethod):
    def arity(self):
        return 2

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        begin, end = arguments
        begin = self.array._validate_index_type(begin)
        end = self.array._validate_index_type(end)
        self.array._check_read_bounds(begin)
        self.array._check_insert_bounds(end)
        return LoxArray(self.array.elements[begin:end])

    def __str__(self):
        return "<array method slice>"


class CopyMethod(BuiltinArrayMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray(self.array.elements)

    def __str__(self):
        return "<array method copy>"


class BuiltinArray(BuiltinClass):
    def __init__(self):
        name = Token(TokenType.IDENTIFIER, "array", None, 0)
        methods = {
            "append": AppendMethod(),
            "pop": PopMethod(),
            "length": LengthMethod(),
            "clear": ClearMethod(),
            "remove": RemoveMethod(),
            "insert": InsertMethod(),
            "index": IndexMethod(),
            "reverse": ReverseMethod(),
            "contains": ContainsMethod(),
            "first": FirstMethod(),
            "last": LastMethod(),
            "remove_at": RemoveAtMethod(),
            "slice": SliceMethod(),
            "copy": CopyMethod(),
        }
        super().__init__(name, methods, None)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray()

    def __str__(self):
        return "<builtin fn array>"


class LoxArray(LoxInstance):
    def __init__(self, elements: List[Any] = []):
        self.elements = list(elements) if elements else []
        super().__init__(BuiltinArray())

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

    def __eq__(self, other):
        return self.elements == other.elements
