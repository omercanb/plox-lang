from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from plox.types import environment, expr
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


class LoxBindableMethod(LoxCallable):
    def bind(self, instance: Any) -> "LoxBindableMethod": ...


class LoxFunction(LoxBindableMethod):
    def __init__(
        self, declaration: "Function", closure: Environment, is_initializer
    ) -> None:
        self.declaration: "Function" = declaration
        self.closure: Environment = closure
        self.is_initializer = is_initializer

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            if self.is_initializer:
                return self.closure.values["this"]
            return e.value

        # Function had no return value
        if self.is_initializer:
            return self.closure.values["this"]
        return None

    def bind(self, instance: "LoxInstance"):
        """Used before calling a method to bind the name 'this' in the method to the instance in which it was called on"""
        environment = Environment(self.closure)
        environment.define("this", instance)
        method = LoxFunction(self.declaration, environment, self.is_initializer)
        return method

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class LoxLambda(LoxCallable):
    def __init__(
        self, params: List[Token], body: expr.Expr, closure: Environment
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
        return_value = interpreter.evaluate_in_environment(self.body, environment)
        return return_value

    def __str__(self) -> str:
        return f"<lambda>"


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: Token,
        methods: Dict[str, LoxBindableMethod],
        superclass: Optional["LoxClass"],
    ):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def __str__(self):
        return f"<class {self.name.lexeme}>"

    def arity(self):
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            instance = initializer.bind(instance).call(interpreter, arguments)
            assert isinstance(instance, LoxInstance)
            return instance
        return instance

    def find_method(self, name: str):
        if method := self.methods.get(name):
            return method

        if self.superclass:
            return self.superclass.find_method(name)

        return None


class LoxInstance:
    def __init__(self, cls: LoxClass):
        self.cls = cls
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        if method := self.cls.find_method(name.lexeme):
            return method.bind(self)
        raise RuntimeError(f"Undefined property {name.lexeme} on '{str(self)}'")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance {self.cls.name.lexeme}>"
