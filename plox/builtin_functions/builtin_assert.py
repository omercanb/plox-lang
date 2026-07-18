from typing import Any, List, TYPE_CHECKING

from plox.types.lox_callable import LoxCallable
from plox.types.lox_error import RuntimeError

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinAssert(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        condition = arguments[0]
        if not interpreter.is_truthy(condition):
            raise RuntimeError(None, "Assertion failed")
        return None

    def __str__(self):
        return "<builtin assert>"
