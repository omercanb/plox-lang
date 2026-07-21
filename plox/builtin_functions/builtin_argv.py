import sys
from typing import TYPE_CHECKING, Any, List

from plox.types.lox_callable import LoxCallable

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinArgv(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> list[str]:
        return sys.argv

    def __str__(self) -> str:
        return "<builtin argv>"
