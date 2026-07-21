from typing import TYPE_CHECKING, Any, Iterable, List, Set

from plox.builtin_functions.builtin_array import LoxArray
from plox.builtin_functions.builtin_classes import BuiltinClass
from plox.builtin_functions.builtin_pair import LoxPair
from plox.builtin_functions.builtin_string import LoxString
from plox.types.lox_callable import LoxBindableMethod, LoxInstance
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinSetMethod(LoxBindableMethod):
    """Base class for set methods"""

    set: "LoxSet"

    def bind(self, instance: "LoxSet"):
        method = type(self)()
        method.set = instance
        return method

    def _other(self, value: Any) -> "LoxSet":
        """Validate that an argument is another set."""
        if not isinstance(value, LoxSet):
            raise RuntimeError(None, "Argument must be a set.")
        return value


class AddMethod(BuiltinSetMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.set.elements.add(self.set._validate_element_type(arguments[0]))
        return None

    def __str__(self):
        return "<set method add>"


class ContainsMethod(BuiltinSetMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return self.set._validate_element_type(arguments[0]) in self.set.elements

    def __str__(self):
        return "<set method contains>"


class RemoveMethod(BuiltinSetMethod):
    """Removes an element, erroring if it isn't present."""

    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        element = self.set._validate_element_type(arguments[0])
        if element not in self.set.elements:
            raise RuntimeError(None, f"Element {element} not in set.")
        self.set.elements.remove(element)
        return None

    def __str__(self):
        return "<set method remove>"


class DiscardMethod(BuiltinSetMethod):
    """Removes an element if present. Returns whether anything was removed."""

    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        element = self.set._validate_element_type(arguments[0])
        if element not in self.set.elements:
            return False
        self.set.elements.discard(element)
        return True

    def __str__(self):
        return "<set method discard>"


class PopMethod(BuiltinSetMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        if len(self.set.elements) == 0:
            raise RuntimeError(None, "Cannot pop from empty set.")
        return self.set.elements.pop()

    def __str__(self):
        return "<set method pop>"


class ClearMethod(BuiltinSetMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.set.elements.clear()
        return None

    def __str__(self):
        return "<set method clear>"


class LengthMethod(BuiltinSetMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return len(self.set.elements)

    def __str__(self):
        return "<set method length>"


class ElementsMethod(BuiltinSetMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray(list(self.set.elements))

    def __str__(self):
        return "<set method elements>"


class CopyMethod(BuiltinSetMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxSet":
        return LoxSet(self.set.elements)

    def __str__(self):
        return "<set method copy>"


class UnionMethod(BuiltinSetMethod):
    """Mutates in place: adds every element of the other set."""

    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.set.elements |= self._other(arguments[0]).elements
        return None

    def __str__(self):
        return "<set method union>"


class IntersectionMethod(BuiltinSetMethod):
    """Mutates in place: keeps only elements also in the other set."""

    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.set.elements &= self._other(arguments[0]).elements
        return None

    def __str__(self):
        return "<set method intersection>"


class DifferenceMethod(BuiltinSetMethod):
    """Mutates in place: removes every element found in the other set."""

    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.set.elements -= self._other(arguments[0]).elements
        return None

    def __str__(self):
        return "<set method difference>"


class BuiltinSet(BuiltinClass):
    def __init__(self):
        name = Token(TokenType.IDENTIFIER, "set", None, 0)
        methods: dict[str, LoxBindableMethod] = {
            "add": AddMethod(),
            "contains": ContainsMethod(),
            "remove": RemoveMethod(),
            "discard": DiscardMethod(),
            "pop": PopMethod(),
            "clear": ClearMethod(),
            "length": LengthMethod(),
            "elements": ElementsMethod(),
            "copy": CopyMethod(),
            "union": UnionMethod(),
            "intersection": IntersectionMethod(),
            "difference": DifferenceMethod(),
        }
        super().__init__(name, methods, None)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxSet":
        return LoxSet()

    def __str__(self):
        return "<builtin fn set>"


class LoxSet(LoxInstance):
    def __init__(self, elements: Iterable[Any] | None = None):
        self.elements: Set[Any] = set(elements) if elements else set()
        super().__init__(BuiltinSet())

    def is_truthy(self) -> bool:
        return len(self.elements) > 0

    def _validate_element_type(self, element: Any) -> Any:
        """Only hashable primitives may be elements. Instances and arrays may not."""
        if element is None or isinstance(
            element, (bool, int, float, LoxString, LoxPair)
        ):
            return element
        raise RuntimeError(
            None, "Set elements must be a number, string, boolean, or nil."
        )

    def __str__(self):
        return "{" + ", ".join(str(e) for e in self.elements) + "}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, LoxSet) and self.elements == other.elements
