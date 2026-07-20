from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

from plox.types.lox_callable import LoxCallable, LoxClass, LoxFunction


class BuiltinFunction(LoxFunction):
    pass


class BuiltinClass(LoxClass):
    pass
