from typing import List, Optional

from plox.types import expr as exprs
from plox.types import stmt as stmts
from plox.types.lox_token import Token
from plox.types.token_type import TokenType


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens
        self.current: int = 0
        self.current_loop_nesting_depth: int = 0

    def parse(self) -> List[stmts.Stmt]:
        statements = []
        while not self.is_at_end():
            statement = self.declaration()
            if statement is not None:
                statements.append(statement)
        return statements

    def declaration(self) -> Optional[stmts.Stmt]:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def class_declaration(self) -> stmts.Class:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expected superclass name after '<'.")
            # Cast a superclass identfier to a variable to make it easier to resolve later
            superclass = exprs.Variable(self.previous())
        else:
            superclass = None

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return stmts.Class(name, methods, superclass)

    # kind is used to distinguish functions, methods, and lambdas
    def function(self, kind: str) -> "stmts.Function | exprs.LambdaFunction":
        name = None
        if kind == "lambda":
            self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind}.")
        else:
            name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
            self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(params) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                params.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        if kind == "lambda":
            return exprs.LambdaFunction(params, body)
        else:
            return stmts.Function(name, params, body)

    def return_(self) -> stmts.Return:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            # An expression is returned
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect newline after return value.")
        return stmts.Return(keyword, value)

    def var_declaration(self, in_for=False) -> stmts.Var:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        if in_for:
            self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        else:
            self.consume(
                TokenType.SEMICOLON, "Expect newline after variable declaration."
            )
        return stmts.Var(name, initializer)

    def statement(self) -> stmts.Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.RETURN):
            return self.return_()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmts.Block(self.block())
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.CONTINUE):
            return self.continue_statement()
        return self.expression_statement()

    def for_statement(self) -> stmts.For:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration(in_for=True)
        else:
            initializer = self.expression_statement(in_for=True)

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        self.current_loop_nesting_depth += 1
        body = self.statement()
        self.current_loop_nesting_depth -= 1

        return stmts.For(initializer, condition, increment, body)

    def if_statement(self) -> stmts.If:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return stmts.If(condition, then_branch, else_branch)

    def while_statement(self) -> stmts.While:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        self.current_loop_nesting_depth += 1
        body = self.statement()
        self.current_loop_nesting_depth -= 1
        return stmts.While(condition, body)

    def break_statement(self) -> stmts.Break:
        if self.current_loop_nesting_depth == 0:
            self.error(self.previous(), "break not in loop.")
        self.consume(TokenType.SEMICOLON, "Expect newline after 'break'.")
        return stmts.Break()

    def continue_statement(self) -> stmts.Continue:
        if self.current_loop_nesting_depth == 0:
            self.error(self.previous(), "continue not in loop.")
        self.consume(TokenType.SEMICOLON, "Expect newline after 'continue'.")
        return stmts.Continue()

    def block(self) -> List[stmts.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self, in_for=False) -> stmts.Expression:
        expression = self.expression()
        if in_for:
            self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        else:
            self.consume(TokenType.SEMICOLON, "Expect newline after expression.")
        return stmts.Expression(expression)

    def expression(self) -> exprs.Expr:
        return self.assignment()

    def assignment(self) -> exprs.Expr:
        COMPOUND_ASSIGN = {
            TokenType.PLUS_EQUAL: TokenType.PLUS,
            TokenType.MINUS_EQUAL: TokenType.MINUS,
            TokenType.STAR_EQUAL: TokenType.STAR,
            TokenType.SLASH_EQUAL: TokenType.SLASH,
            TokenType.MODULO_EQUAL: TokenType.MODULO,
        }

        expr = self.or_()
        if self.match(*COMPOUND_ASSIGN):
            op_token = self.previous()
            base_type = COMPOUND_ASSIGN[op_token.token_type]
            value = self.assignment()
            if isinstance(expr, exprs.Variable):
                base_op = Token(base_type, op_token.lexeme[0], None, op_token.line)
                return exprs.Assign(expr.name, exprs.Binary(expr, base_op, value))
            self.error(op_token, "Invalid assignment target.")

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, exprs.Variable):
                return exprs.Assign(expr.name, value)
            elif isinstance(expr, exprs.Get):
                return exprs.Set(expr.object, expr.name, value)
            self.error(equals, "Invalid assignment target.")

        return expr

    def or_(self) -> exprs.Expr:
        expr = self.and_()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.and_()
            expr = exprs.Logical(expr, op, right)
        return expr

    def and_(self) -> exprs.Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = exprs.Logical(expr, op, right)
        return expr

    def equality(self) -> exprs.Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self.previous()
            right = self.comparison()
            expr = exprs.Binary(expr, op, right)
        return expr

    def comparison(self) -> exprs.Expr:
        expr = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            op = self.previous()
            right = self.term()
            expr = exprs.Binary(expr, op, right)
        return expr

    def term(self) -> exprs.Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            op = self.previous()
            right = self.factor()
            expr = exprs.Binary(expr, op, right)
        return expr

    def factor(self) -> exprs.Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            op = self.previous()
            right = self.unary()
            expr = exprs.Binary(expr, op, right)
        return expr

    def unary(self) -> exprs.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            op = self.previous()
            right = self.unary()
            return exprs.Unary(op, right)
        return self.call()

    def call(self) -> exprs.Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                property = self.consume(
                    TokenType.IDENTIFIER, "Expected identifier after '.'."
                )
                expr = exprs.Get(expr, property)
            else:
                break
        return expr

    def finish_call(self, callee: exprs.Expr) -> exprs.Call:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return exprs.Call(callee, paren, arguments)

    def primary(self) -> exprs.Expr:
        if self.match(TokenType.FALSE):
            return exprs.Literal(False)
        if self.match(TokenType.TRUE):
            return exprs.Literal(True)
        if self.match(TokenType.NIL):
            return exprs.Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return exprs.Literal(self.previous().literal)
        if self.match(TokenType.THIS):
            return exprs.This(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return exprs.Variable(self.previous())
        if self.match(TokenType.FUN):
            return self.function("lambda")
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return exprs.Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        from plox import plox

        plox.error(token.line, message)
        raise ParseError()

    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in [
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
            ]:
                return
            self.advance()
