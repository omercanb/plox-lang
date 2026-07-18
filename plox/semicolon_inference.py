from typing import List

from plox.types.token_type import TokenType


class SemicolonInference:
    """Handles semicolon inference logic"""

    def __init__(self):
        self.paren_depth = 0
        self.brace_stack: List[str] = []  # Track "lambda" or "block"
        self.last_was_fun = False  # Track if we just saw 'fun' keyword
        self.last_closed_brace_type = ""  # Track what type of brace we just closed

    def update(self, token_type: TokenType) -> None:
        """Update internal state with a new token"""
        if token_type == TokenType.LEFT_PAREN:
            self.paren_depth += 1
        elif token_type == TokenType.RIGHT_PAREN:
            self.paren_depth -= 1
        elif token_type == TokenType.FUN:
            self.last_was_fun = True
        elif token_type == TokenType.IDENTIFIER and self.paren_depth == 0:
            # Reset only if identifier at depth 0 (function name after 'fun')
            self.last_was_fun = False
        elif token_type == TokenType.LEFT_BRACE:
            self._track_brace_open()
        elif token_type == TokenType.RIGHT_BRACE:
            self.last_closed_brace_type = self._track_brace_close()

    def should_add_semicolon_before_newline(self, last_token_type: TokenType) -> bool:
        """Determine if semicolon should be added before a newline"""
        if last_token_type == TokenType.RIGHT_BRACE:
            # We closed a lambda but it's not in a function call
            if self.last_closed_brace_type == "lambda" and self.paren_depth == 0:
                return True
            self.last_closed_brace_type = ""
            return False

        # Shouldn't open a semicolon after a '{'
        if (
            last_token_type == TokenType.SEMICOLON
            or last_token_type == TokenType.LEFT_BRACE
        ):
            return False

        # Not in a function call means a semicolon can be safely added
        if self.paren_depth == 0:
            return True

        # Inside a function call semicolons should never be added
        if self.paren_depth > 0:
            return False

        return False

    def _track_brace_open(self) -> None:
        """Determine and track what type of brace is opening"""
        # Check if this is a lambda: we saw 'fun' without an identifier between fun and (
        if self.last_was_fun:
            self.brace_stack.append("lambda")
        else:
            self.brace_stack.append("block")
        self.last_was_fun = False

    def _track_brace_close(self) -> str:
        """Pop and return what type of brace is closing"""
        if self.brace_stack:
            return self.brace_stack.pop()
        return "block"
