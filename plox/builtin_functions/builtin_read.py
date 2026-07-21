from typing import TYPE_CHECKING, Any, List

from plox.builtin_functions.builtin_array import LoxArray
from plox.types.lox_callable import LoxCallable
from plox.types.lox_error import RuntimeError

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinRead(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> str:
        path = arguments[0]
        try:
            return open(path).read()
        except Exception as e:
            print(e)
            raise RuntimeError(None, f"File '{path}' can't be opened")

    def __str__(self) -> str:
        return "<builtin read>"


class BuiltinReadLines(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> LoxArray:
        path = arguments[0]
        try:
            return LoxArray(open(path).read().splitlines())
        except Exception:
            raise RuntimeError(None, f"File '{path}' can't be opened")

    def __str__(self) -> str:
        return "<builtin readlines>"
