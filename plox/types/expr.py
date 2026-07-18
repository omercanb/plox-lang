from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    import plox.types.stmt as stmt
    from plox.types.lox_token import Token


@dataclass(eq=False)
class Expr:
    pass


@dataclass(eq=False)
class Assign(Expr):
    name: "Token"
    value: Expr


@dataclass(eq=False)
class Binary(Expr):
    left: Expr
    op: "Token"
    right: Expr


@dataclass(eq=False)
class Logical(Expr):
    left: Expr
    op: "Token"
    right: Expr


@dataclass(eq=False)
class Unary(Expr):
    op: "Token"
    right: Expr


@dataclass(eq=False)
class Grouping(Expr):
    expr: Expr


@dataclass(eq=False)
class Literal(Expr):
    value: Any


@dataclass(eq=False)
class Variable(Expr):
    name: "Token"


@dataclass(eq=False)
class Call(Expr):
    callee: Expr
    paren: "Token"
    arguments: List[Expr]


@dataclass(eq=False)
class Get(Expr):
    object: Expr
    name: "Token"


@dataclass(eq=False)
class LambdaFunction(Expr):
    params: List["Token"]
    body: List["stmt.Stmt"]
