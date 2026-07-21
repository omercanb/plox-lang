from typing import Any, Dict, List

from plox.builtin_functions.builtin_array import BuiltinArray
from plox.builtin_functions.builtin_assert import BuiltinAssert
from plox.builtin_functions.builtin_clock import BuiltinClock
from plox.builtin_functions.builtin_map import BuiltinMap
from plox.builtin_functions.builtin_pair import BuiltinPair
from plox.builtin_functions.builtin_print import BuiltinPrint
from plox.builtin_functions.builtin_read import BuiltinRead, BuiltinReadLines
from plox.builtin_functions.builtin_set import BuiltinSet
from plox.types import environment, expr, stmt
from plox.types.control_flow import BreakException, ContinueException, ReturnException
from plox.types.environment import Environment
from plox.types.lox_callable import (
    LoxCallable,
    LoxClass,
    LoxFunction,
    LoxInstance,
    LoxLambda,
)
from plox.types.lox_error import RuntimeError
from plox.types.lox_token import Token
from plox.types.token_type import TokenType


class Interpreter:
    def __init__(self, locals: dict[Token, int]) -> None:
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.globals.define("clock", BuiltinClock())
        self.globals.define("print", BuiltinPrint())
        self.globals.define("array", BuiltinArray())
        self.globals.define("map", BuiltinMap())
        self.globals.define("pair", BuiltinPair())
        self.globals.define("set", BuiltinSet())
        self.globals.define("assert", BuiltinAssert())
        self.globals.define("read", BuiltinRead())
        self.globals.define("readlines", BuiltinReadLines())
        # A mapping of variables to how many scopes up the variable was defined
        self.locals: dict[Token, int] = locals

    def get_variable(self, name: Token):
        if name in self.locals:
            distance = self.locals[name]
            return self.environment.get_at(name.lexeme, distance)
        else:
            if name.lexeme in self.globals.values:
                return self.globals.get_at(name.lexeme, 0)
            else:
                raise RuntimeError(name, "Variable undefined")

    def push_environment(self):
        self.environment = Environment(self.environment)

    def pop_environment(self):
        assert self.environment.enclosing
        self.environment = self.environment.enclosing

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            from plox import plox

            plox.runtime_error(error)

    def execute(self, statement: stmt.Stmt) -> None:
        self.visit(statement)

    def evaluate(self, expression: expr.Expr) -> Any:
        return self.visit(expression)

    def evaluate_in_environment(
        self, expression: expr.Expr, environment: Environment
    ) -> Any:
        previous = self.environment
        try:
            self.environment = environment
            return self.visit(expression)
        finally:
            self.environment = previous

    def visit(self, node: Any) -> Any:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"No visitor for {type(node).__name__}")
        return method(node)

    def execute_block(
        self, statements: List[stmt.Stmt], environment: Environment
    ) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    # Expression visitors
    def visit_Assign(self, node: expr.Assign) -> Any:
        value = self.evaluate(node.value)
        distance = self.locals.get(node.name)
        if distance is not None:
            self.environment.assign_at(node.name, value, self.locals[node.name])
        else:
            self.globals.assign(node.name, value)
        return value

    def visit_Binary(self, node: expr.Binary) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        token_type = node.op.token_type
        if token_type == TokenType.GREATER:
            self.check_number_operands(node.op, left, right)
            return left > right
        elif token_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(node.op, left, right)
            return left >= right
        elif token_type == TokenType.LESS:
            self.check_number_operands(node.op, left, right)
            return left < right
        elif token_type == TokenType.LESS_EQUAL:
            self.check_number_operands(node.op, left, right)
            return left <= right
        elif token_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif token_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        elif token_type == TokenType.MINUS:
            self.check_number_operands(node.op, left, right)
            return left - right
        elif token_type == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) or isinstance(right, str):
                return self.stringify(left) + self.stringify(right)
            raise RuntimeError(node.op, "Operands must be two numbers or two strings.")
        elif token_type == TokenType.SLASH:
            self.check_number_operands(node.op, left, right)
            if right == 0:
                raise RuntimeError(node.op, "Division by zero.")
            return left / right
        elif token_type == TokenType.STAR:
            self.check_number_operands(node.op, left, right)
            return left * right
        elif token_type == TokenType.MODULO:
            self.check_number_operands(node.op, left, right)
            if right == 0:
                raise RuntimeError(node.op, "Modulo by zero.")
            return left % right
        return None

    def visit_Logical(self, node: expr.Logical) -> Any:
        left: Any = self.evaluate(node.left)
        if node.op.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(node.right)

    def visit_Unary(self, node: expr.Unary) -> Any:
        right = self.evaluate(node.right)
        token_type = node.op.token_type
        if token_type == TokenType.BANG:
            return not self.is_truthy(right)
        elif token_type == TokenType.MINUS:
            self.check_number_operand(node.op, right)
            return -right
        return None

    def visit_Grouping(self, node: expr.Grouping) -> Any:
        return self.evaluate(node.expr)

    def visit_Literal(self, node: expr.Literal) -> Any:
        return node.value

    def visit_Variable(self, node: expr.Variable) -> Any:
        return self.get_variable(node.name)

    def visit_This(self, node: expr.This):
        return self.get_variable(node.keyword)

    def visit_Super(self, node: expr.Super):
        distance = self.locals[node.keyword]
        superclass = self.environment.get_at("super", distance)
        assert isinstance(superclass, LoxClass)
        # distance - 1 to get 'this' which is in the inner environment
        this = self.environment.get_at("this", distance - 1)
        method = superclass.find_method(node.method.lexeme)
        if not method:
            raise RuntimeError(
                node.method, f"Undefined property '{node.method.lexeme}'."
            )
        return method.bind(this)

    def visit_Lambda(self, node: expr.Lambda):
        function = LoxLambda(node.params, node.body, self.environment)
        return function

    def visit_Call(self, node: expr.Call) -> Any:
        callee: Any = self.evaluate(node.callee)
        arguments: List[Any] = [self.evaluate(arg) for arg in node.arguments]
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(
                node.callee,
                f"Can only call functions and classes. Called on {type(callee)}",
            )
        if len(arguments) != callee.arity():
            raise RuntimeError(
                node.callee,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )
        return callee.call(self, arguments)

    def visit_Get(self, node: expr.Get):
        object = self.evaluate(node.object)
        if not isinstance(object, LoxInstance):
            raise RuntimeError(node.name, "Only instances have properties.")
        return object.get(node.name)

    def visit_Set(self, node: expr.Set):
        object = self.evaluate(node.object)
        if not isinstance(object, LoxInstance):
            raise RuntimeError(node.name, "Only instances have properties.")
        value = self.evaluate(node.value)
        object.set(node.name, value)
        return value

    def visit_Index(self, node: expr.Index):
        obj = self.evaluate(node.object)
        index = self.evaluate(node.index)

        if hasattr(obj, "get_index") and callable(getattr(obj, "get_index")):
            return obj.get_index(node.bracket, index)

        raise RuntimeError(node.object, "Doesn't support indexing.")

    def visit_IndexAssign(self, node: expr.IndexAssign):
        obj = self.evaluate(node.object)
        index = self.evaluate(node.index)
        value = self.evaluate(node.value)

        if hasattr(obj, "set_index") and callable(getattr(obj, "set_index")):
            return obj.set_index(node.bracket, index, value)

        raise RuntimeError(node.object, "Doesn't support indexing.")

    # Statement visitors
    def visit_Expression(self, node: stmt.Expression) -> None:
        self.evaluate(node.expr)

    def visit_Var(self, node: stmt.Var) -> None:
        value: Any = None
        if node.initializer is not None:
            value = self.evaluate(node.initializer)
        self.environment.define(node.name.lexeme, value)

    def visit_If(self, node: stmt.If) -> None:
        if self.is_truthy(self.evaluate(node.condition)):
            self.execute(node.then_branch)
        elif node.else_branch is not None:
            self.execute(node.else_branch)

    def visit_While(self, node: stmt.While) -> None:
        while self.is_truthy(self.evaluate(node.condition)):
            try:
                self.execute(node.body)
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_For(self, node: stmt.For) -> None:
        self.push_environment()
        if node.initializer is not None:
            self.execute(node.initializer)
        while node.condition is None or self.is_truthy(self.evaluate(node.condition)):
            try:
                self.execute(node.body)
            except BreakException:
                break
            except ContinueException:
                pass
            if node.increment is not None:
                self.evaluate(node.increment)
        self.pop_environment()

    def visit_Class(self, node: stmt.Class):
        if node.superclass:
            superclass = self.evaluate(node.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(node.superclass.name, "Superclass must be a class.")
        else:
            superclass = None

        # First declare the class name so it can be referenced inside the class
        self.environment.define(node.name.lexeme, None)

        # Create a scope for the super to match the resolver
        # We need to resolve 'super' based on the class of the method using super, not the instance in which this method is used
        if superclass:
            self.push_environment()
            self.environment.define("super", superclass)

        methods: Dict[str, LoxFunction] = {}
        for method in node.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function

        if superclass:
            self.pop_environment()

        cls = LoxClass(node.name, methods, superclass)

        self.environment.assign(node.name, cls)

        pass

    def visit_Function(self, node: stmt.Function) -> None:
        function = LoxFunction(node, self.environment, is_initializer=False)
        self.environment.define(node.name.lexeme, function)

    def visit_Return(self, node: stmt.Return) -> None:
        value: Any = None
        if node.value != None:
            value = self.evaluate(node.value)
        raise ReturnException(value)

    def visit_Break(self, node: stmt.Break) -> None:
        raise BreakException()

    def visit_Continue(self, node: stmt.Continue) -> None:
        raise ContinueException()

    def visit_Block(self, node: stmt.Block) -> None:
        self.execute_block(node.statements, Environment(self.environment))

    # Helpers
    def is_truthy(self, value: Any) -> bool:
        if value is None or value is False:
            return False
        if hasattr(value, "is_truthy") and callable(getattr(value, "is_truthy")):
            return value.is_truthy()
        return True

    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a == b

    def check_number_operand(self, op: Token, operand: Any) -> None:
        if isinstance(operand, (int, float)):
            return
        raise RuntimeError(op, "Operand must be a number.")

    def check_number_operands(self, op: Token, left: Any, right: Any) -> None:
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(op, "Operands must be numbers.")

    def stringify(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                return text[:-2]
            return text
        return str(value)
