import sys
from typing import TYPE_CHECKING, Any, List

from plox.builtin_functions.builtin_array import LoxArray
from plox.builtin_functions.builtin_string import LoxString
from plox.types.lox_callable import LoxCallable

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinArgv(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> LoxArray:
        return LoxArray([LoxString(arg) for arg in sys.argv[1:]])

    def __str__(self) -> str:
        return "<builtin argv>"
