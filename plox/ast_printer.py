from typing import Any

from plox.types import expr as expr
from plox.types import stmt as stmt
from plox.types.lox_token import Token


class AstPrinter:
    def print_stmt(self, statement: stmt.Stmt) -> None:
        print(self.visit(statement))

    def print_expr(self, expression: expr.Expr) -> None:
        print(self.visit(expression))

    def visit(self, node: Any) -> str:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"No visitor for {type(node).__name__}")
        return method(node)

    def visit_Token(self, node: Token):
        return node.lexeme

    # Expression visitors
    def visit_Assign(self, node: expr.Assign) -> str:
        return self.parenthesize(f"assign {node.name.lexeme}", node.value)

    def visit_Binary(self, node: expr.Binary) -> str:
        return self.parenthesize(node.op.lexeme, node.left, node.right)

    def visit_Logical(self, node: expr.Logical) -> str:
        return self.parenthesize(node.op.lexeme, node.left, node.right)

    def visit_Unary(self, node: expr.Unary) -> str:
        return self.parenthesize(node.op.lexeme, node.right)

    def visit_Grouping(self, node: expr.Grouping) -> str:
        return self.parenthesize("group", node.expr)

    def visit_Literal(self, node: expr.Literal) -> str:
        if node.value is None:
            return "nil"
        return str(node.value)

    def visit_Variable(self, node: expr.Variable) -> str:
        return node.name.lexeme

    def visit_This(self, node: expr.This):
        return "this"

    def visit_Super(self, node: expr.Super):
        return f"super.{self.visit(node.method)}"

    def visit_Call(self, node: expr.Call) -> str:
        result = self.parenthesize("call", node.callee, *node.arguments)
        return result

    def visit_LambdaFunction(self, node: expr.LambdaFunction) -> str:
        return (
            "(lambda "
            + "(params "
            + " ".join([param.lexeme for param in node.params])
            + ") "
            + self.parenthesize("body", *node.body)
            + ")"
        )

    def visit_Get(self, node: expr.Get):
        return f"({self.visit(node.object)}.{self.visit(node.name)})"

    def visit_Set(self, node: expr.Set):
        return f"({self.visit(node.object)}.{self.visit(node.name)} = {self.visit(node.value)})"

    # Statement visitors
    def visit_Expression(self, node: stmt.Expression) -> str:
        return self.visit(node.expr)

    def visit_Var(self, node: stmt.Var) -> str:
        if node.initializer is None:
            return f"(var {node.name.lexeme})"
        return f"(var {node.name.lexeme} = {self.visit(node.initializer)})"

    def visit_If(self, node: stmt.If) -> str:
        if node.else_branch is None:
            return self.parenthesize("if", node.condition, node.then_branch)
        return self.parenthesize(
            "if", node.condition, node.then_branch, node.else_branch
        )

    def visit_While(self, node: stmt.While) -> str:
        return self.parenthesize("while", node.condition, node.body)

    def visit_For(self, node: stmt.For) -> str:
        parts = [node.initializer, node.condition, node.increment, node.body]
        return self.parenthesize("for", *[p for p in parts if p is not None])

    def visit_Function(self, node: stmt.Function) -> str:
        return (
            "(function "
            + node.name.lexeme
            + " "
            + "(params "
            + " ".join([param.lexeme for param in node.params])
            + ") "
            + self.parenthesize("body", *node.body)
            + ")"
        )

    def visit_Class(self, node: stmt.Class):
        s = f"(class {node.name.lexeme} (methods "
        for method in node.methods:
            s += self.visit(method)
        s += ")"
        return s

    def visit_Return(self, node: stmt.Return) -> str:
        return self.parenthesize("return", node.value)

    def visit_Break(self, node: stmt.Break) -> str:
        return "break"

    def visit_Continue(self, node: stmt.Continue) -> str:
        return "continue"

    def visit_Block(self, node: stmt.Block) -> str:
        items: str = " ".join(self.visit(stmt) for stmt in node.statements)
        return f"{{ {items} }}"

    def parenthesize(self, name: str, *exprs: Any) -> str:
        result = f"({name}"
        for expr in exprs:
            if expr is None:
                continue
            result += f" {self.visit(expr)}"
        result += ")"
        return result
