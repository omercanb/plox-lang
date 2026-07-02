from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from plox.types.expr import Expr
    from plox.types.lox_token import Token


@dataclass(eq=False)
class Stmt:
    pass


@dataclass(eq=False)
class Expression(Stmt):
    expr: "Expr"


@dataclass(eq=False)
class Print(Stmt):
    expr: "Expr"


@dataclass(eq=False)
class Var(Stmt):
    name: "Token"
    initializer: Optional["Expr"]


@dataclass(eq=False)
class If(Stmt):
    condition: "Expr"
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass(eq=False)
class While(Stmt):
    condition: "Expr"
    body: Stmt


@dataclass(eq=False)
class For(Stmt):
    initializer: Optional[Stmt]
    condition: Optional["Expr"]
    increment: Optional["Expr"]
    body: Stmt


@dataclass(eq=False)
class Function(Stmt):
    name: "Token"
    params: List["Token"]
    body: List["Stmt"]


@dataclass(eq=False)
class Return(Stmt):
    keyword: "Token"
    value: Optional["Expr"]
    pass


@dataclass(eq=False)
class Break(Stmt):
    pass


@dataclass(eq=False)
class Continue(Stmt):
    pass


@dataclass(eq=False)
class Block(Stmt):
    statements: List["Stmt"]
