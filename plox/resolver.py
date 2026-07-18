import dataclasses
from dataclasses import dataclass

import plox.types.expr as expr
import plox.types.stmt as stmt
from plox.types.environment import Environment
from plox.types.lox_error import StaticError
from plox.types.lox_token import Token

# Walk the ast and resolve all variables to their definitions


@dataclass
class Scope:
    enclosing: "Scope | None" = None
    bindings: dict[str, bool] = dataclasses.field(default_factory=dict)

    def declare(self, name: Token):
        assert name.lexeme not in self.bindings
        self.bindings[name.lexeme] = False

    # Distinct declare and defined allow us to raise undefined variable errors
    def define(self, name: Token):
        assert name.lexeme in self.bindings
        self.bindings[name.lexeme] = True

    def declare_define(self, name: Token):
        self.declare(name)
        self.define(name)

    # Returns how many scopes above the curent the variable was defined
    # or returns none if not found
    def resolve(self, name: Token, distance=0) -> int | None:
        if name.lexeme in self.bindings:
            if self.bindings[name.lexeme] is False:
                raise StaticError(name, "Variable declared but not defined before use")
            else:
                return distance
        if self.enclosing:
            return self.enclosing.resolve(name, distance + 1)
        else:
            return None


# Must keep track of definititons and variable usages
@dataclass
class ScopeResolver:
    scope: Scope = dataclasses.field(default_factory=Scope)
    # The distance to the enclosing scope in which the variable was defined
    locals: dict[Token, int] = dataclasses.field(default_factory=dict)

    def resolve_local(self, name: Token):
        assert name not in self.locals
        result = self.scope.resolve(name)
        if result is not None:
            distance = result
            self.locals[name] = distance

    def visit(self, node):
        if node is None:
            return
        if isinstance(node, list):
            for child in node:
                self.visit(child)
        else:
            method_name = f"visit_{type(node).__name__}"
            method = getattr(self, method_name, self.generic_visit)
            method(node)

    def generic_visit(self, node):
        if node is None:
            return
        if isinstance(node, list):
            for child in node:
                self.visit(child)
        else:
            fields = dataclasses.fields(node)
            for field in fields:
                value = getattr(node, field.name)
                if (
                    isinstance(value, stmt.Stmt)
                    or isinstance(value, expr.Expr)
                    or isinstance(value, list)
                ):
                    self.visit(value)

    def push_scope(self):
        self.scope = Scope(self.scope)

    def pop_scope(self):
        assert self.scope.enclosing is not None
        self.scope = self.scope.enclosing

    def resolve_function(self, node: stmt.Function, function_type: str):
        self.scope.declare_define(node.name)
        self.push_scope()
        for param in node.params:
            self.scope.declare_define(param)
        self.visit(node.body)
        self.pop_scope()

    # Constructs that create a new scope
    def visit_Block(self, node: stmt.Block):
        self.push_scope()
        self.visit(node.statements)
        self.pop_scope()

    # For loop creates a scope, then the body is another scope if it's a block
    def visit_For(self, node: stmt.For):
        self.push_scope()
        self.visit(node.initializer)
        self.visit(node.condition)
        self.visit(node.increment)
        self.visit(node.body)
        self.pop_scope()

    def visit_Class(self, node: stmt.Class):
        self.scope.declare_define(node.name)
        self.push_scope()
        # Step over the define function because that is for language users
        self.scope.bindings["this"] = True
        for method in node.methods:
            self.resolve_function(method, "method")
        self.pop_scope()

    def visit_This(self, node: expr.This):
        self.resolve_local(node.keyword)

    def visit_Function(self, node: stmt.Function):
        self.resolve_function(node, "function")

    def visit_LambdaFunction(self, node: expr.LambdaFunction):
        self.push_scope()
        for param in node.params:
            self.scope.declare_define(param)
        self.visit(node.body)
        self.pop_scope()

    # Constructs that define a variable
    def visit_Var(self, node: stmt.Var):
        self.scope.declare(node.name)
        self.visit(node.initializer)
        self.scope.define(node.name)

    # Consstructs that use a variable
    def visit_Variable(self, node: expr.Variable):
        self.resolve_local(node.name)

    def visit_Assign(self, node: expr.Assign):
        self.visit(node.value)
        self.resolve_local(node.name)
