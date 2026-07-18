from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

from plox.types import stmt
from plox.types.control_flow import ReturnException
from plox.types.environment import Environment
from plox.types.lox_token import Token
from plox.types.stmt import Function, Stmt

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        pass

    def __str__(self) -> str:
        return "<callable>"


class LoxFunction(LoxCallable):
    def __init__(self, declaration: "Function", closure: Environment) -> None:
        self.declaration: "Function" = declaration
        self.closure: Environment = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value

        # Function had no return value
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class LoxLambda(LoxCallable):
    def __init__(
        self, params: List[Token], body: List[Stmt], closure: Environment
    ) -> None:
        self.params = params
        self.body = body
        self.closure: Environment = closure

    def arity(self) -> int:
        return len(self.params)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        for param, arg in zip(self.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.body, environment)
        except ReturnException as e:
            return e.value

        # Function had no return value
        return None

    def __str__(self) -> str:
        return f"<lambda>"


class LoxClass(LoxCallable):
    def __init__(self, node: stmt.Class):
        self.name = node.name
        self.methods = node.methods

    def __str__(self):
        return f"<class {self.name.lexeme}>"

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return LoxInstance(self)


class LoxInstance:
    def __init__(self, cls: LoxClass):
        self.cls = cls
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme not in self.fields:
            raise RuntimeError(f"Undefined property {name.lexeme} on '{str(self)}'")
        return self.fields[name.lexeme]

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance {self.cls.name.lexeme}>"
