from typing import TYPE_CHECKING, Any, Dict, List

from plox.builtin_functions.builtin_array import LoxArray
from plox.builtin_functions.builtin_classes import BuiltinClass
from plox.builtin_functions.builtin_pair import BuiltinPair, LoxPair
from plox.builtin_functions.builtin_string import LoxString
from plox.types.lox_callable import LoxBindableMethod, LoxCallable, LoxInstance
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinMapMethod(LoxBindableMethod):
    """Base class for map methods"""

    map: "LoxMap"

    def bind(self, instance: "LoxMap"):
        method = type(self)()
        method.map = instance
        return method


class GetMethod(BuiltinMapMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        key = arguments[0]
        return self.map.entries.get(self.map._validate_key_type(key))

    def __str__(self):
        return "<map method get>"


class ContainsMethod(BuiltinMapMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return self.map._validate_key_type(arguments[0]) in self.map.entries

    def __str__(self):
        return "<map method contains>"


class RemoveMethod(BuiltinMapMethod):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        key = self.map._validate_key_type(arguments[0])
        if key not in self.map.entries:
            return False
        del self.map.entries[key]
        return True

    def __str__(self):
        return "<map method remove>"


class LengthMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        return len(self.map.entries)

    def __str__(self):
        return "<map method length>"


class ClearMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]):
        self.map.entries.clear()
        return None

    def __str__(self):
        return "<map method clear>"


class KeysMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray(list(self.map.entries.keys()))

    def __str__(self):
        return "<map method keys>"


class ValuesMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray(list(self.map.entries.values()))

    def __str__(self):
        return "<map method values>"


class ItemsMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxArray":
        return LoxArray([LoxPair(k, v) for k, v in self.map.entries.items()])

    def __str__(self):
        return "<map method entries>"


class CopyMethod(BuiltinMapMethod):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxMap":
        return LoxMap(self.map.entries)

    def __str__(self):
        return "<map method copy>"


class BuiltinMap(BuiltinClass):
    def __init__(self):
        name = Token(TokenType.IDENTIFIER, "map", None, 0)
        methods: dict[str, LoxBindableMethod] = {
            "get": GetMethod(),
            "contains": ContainsMethod(),
            "remove": RemoveMethod(),
            "length": LengthMethod(),
            "clear": ClearMethod(),
            "keys": KeysMethod(),
            "values": ValuesMethod(),
            "items": ItemsMethod(),
            "copy": CopyMethod(),
        }
        super().__init__(name, methods, None)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> "LoxMap":
        return LoxMap()

    def __str__(self):
        return "<builtin fn map>"


class LoxMap(LoxInstance):
    def __init__(self, entries: Dict[Any, Any] | None = None):
        self.entries: Dict[Any, Any] = dict(entries) if entries else {}
        super().__init__(BuiltinMap())

    def is_truthy(self) -> bool:
        return len(self.entries) > 0

    def _validate_key_type(self, key: Any) -> Any:
        """Only hashable primitives may be keys. Instances and arrays may not."""
        if key is None or isinstance(key, (bool, int, float, BuiltinPair, LoxString)):
            return key
        raise RuntimeError(None, "Map keys must be a number, string, boolean, or nil.")

    def _show(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def get_index(self, token: Token, index: Any) -> Any:
        key = self._validate_key_type(index)
        if key not in self.entries:
            raise RuntimeError(token, f"Key {self._show(key)} not found.")
        return self.entries[key]

    def set_index(self, token: Token, index: Any, value: Any) -> Any:
        self.entries[self._validate_key_type(index)] = value
        return value

    def __str__(self):
        body = ", ".join(
            f"{self._show(k)}: {self._show(v)}" for k, v in self.entries.items()
        )
        return "{" + body + "}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, LoxMap) and self.entries == other.entries
