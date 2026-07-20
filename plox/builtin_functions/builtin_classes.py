from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

from plox.types.lox_callable import LoxCallable, LoxClass, LoxFunction


class BuiltinMethod(LoxCallable, ABC):

    @abstractmethod
    def bind(self, receiver: Any) -> "BuiltinMethod":
        pass


class BuiltinFunction(LoxFunction):
    pass


class BuiltinClass(LoxClass):
    pass
