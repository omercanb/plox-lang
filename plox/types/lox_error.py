from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from plox.ast_printer import AstPrinter
from plox.types import expr
from plox.types.lox_token import Token


class LoxError(ABC, Exception):
    def __init__(self, node: Optional[Union["Token", "expr.Expr"]], message: str):
        self.node = node
        self.message = message

    def __str__(self):
        if self.node:
            if isinstance(self.node, Token):
                return f"Line {self.node.line} On '{self.node.lexeme}' Error: {self.message}"
            if isinstance(self.node, expr.Expr):
                return f"Error on {AstPrinter().visit(self.node)}: {self.message}"
        else:
            return f"Error: {self.message}"


class RuntimeError(LoxError):
    def __init__(
        self, node: Optional[Union["Token", "expr.Expr"]], message: str
    ) -> None:
        super().__init__(node, message)
        self.message: str = message


class StaticError(LoxError):
    def __init__(
        self, node: Optional[Union["Token", "expr.Expr"]], message: str
    ) -> None:
        super().__init__(node, message)
        self.message: str = message
