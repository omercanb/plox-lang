from typing import TYPE_CHECKING, Any, List

from plox.types.lox_callable import LoxCallable

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class BuiltinPrint(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> None:
        print(interpreter.stringify(arguments[0]).value)
        return None

    def __str__(self) -> str:
        return "<builtin print>"
