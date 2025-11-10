"""
DSL (Domain Specific Language) parser for context filters.

Parses filter expressions like:
- "user.mood == 'happy' AND time.hour < 22"
- "priority >= 5 OR location.city == 'NYC'"
"""

import ast
import operator
import re
from typing import Any


class FilterDSL:
    """
    Parser for context filter DSL expressions.

    Supports:
    - Comparison operators: ==, !=, <, <=, >, >=
    - Logical operators: AND, OR, NOT
    - Path access: user.mood, location.city
    - String, int, float literals
    - Boolean literals: true, false

    Example:
        >>> dsl = FilterDSL()
        >>> filter_func = dsl.parse("user.age >= 18 AND user.verified == true")
        >>> context = {"user": {"age": 25, "verified": True}}
        >>> filter_func(context)  # Returns True
    """

    # Operators mapping
    OPERATORS = {
        "==": operator.eq,
        "!=": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "AND": operator.and_,
        "OR": operator.or_,
        "NOT": operator.not_,
    }

    def __init__(self):
        """Initialize DSL parser."""
        pass

    def parse(self, expression: str) -> callable:
        """
        Parse DSL expression into a filter function.

        Args:
            expression: DSL filter expression string

        Returns:
            Callable that takes context dict and returns bool

        Raises:
            SyntaxError: If expression is invalid

        Example:
            >>> dsl = FilterDSL()
            >>> func = dsl.parse("user.mood == 'happy'")
            >>> func({"user": {"mood": "happy"}})
            True
        """
        if not expression or not expression.strip():
            # Empty expression always returns True
            return lambda ctx: True

        try:
            # Normalize expression
            normalized = self._normalize_expression(expression)

            # Parse into AST
            tree = ast.parse(normalized, mode="eval")

            # Create evaluator function
            def evaluator(context: dict[str, Any]) -> bool:
                try:
                    return self._evaluate_node(tree.body, context)
                except (KeyError, TypeError, AttributeError):
                    # If context path doesn't exist or type mismatch, return False
                    return False

            return evaluator

        except SyntaxError as e:
            raise SyntaxError(f"Invalid filter expression: {expression}") from e

    def _normalize_expression(self, expr: str) -> str:
        """
        Normalize expression for Python AST parsing.

        Converts DSL syntax to Python syntax:
        - "user.mood" -> _ctx_get('user.mood')
        - "priority" -> _ctx_get('priority')
        - "true/false" -> True/False
        - "AND/OR/NOT" -> and/or/not

        Protects string literals during transformation.
        """
        # Step 1: Extract and protect string literals
        strings = []
        string_pattern = r"'[^']*'|\"[^\"]*\""

        def save_string(match):
            strings.append(match.group(0))
            return f"__STRING_{len(strings)-1}__"

        expr = re.sub(string_pattern, save_string, expr)

        # Step 2: Replace boolean literals
        expr = re.sub(r"\btrue\b", "True", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bfalse\b", "False", expr, flags=re.IGNORECASE)

        # Step 3: Replace logical operators
        expr = re.sub(r"\bAND\b", "and", expr)
        expr = re.sub(r"\bOR\b", "or", expr)
        expr = re.sub(r"\bNOT\b", "not", expr)

        # Step 4: Replace context variable access
        def replace_var(match):
            var = match.group(1)
            # Skip keywords, string placeholders, and already wrapped
            if (
                var in ("True", "False", "None", "and", "or", "not")
                or var.startswith("_ctx_get")
                or var.startswith("__STRING_")
            ):
                return var
            return f"_ctx_get('{var}')"

        # Match word or word.word.word patterns (variable paths)
        expr = re.sub(
            r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\b(?!\s*\()", replace_var, expr
        )

        # Step 5: Restore string literals
        for i, string in enumerate(strings):
            expr = expr.replace(f"__STRING_{i}__", string)

        return expr

    def _evaluate_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        """
        Recursively evaluate AST node.

        Args:
            node: AST node to evaluate
            context: Context dictionary

        Returns:
            Evaluation result
        """
        if isinstance(node, ast.BoolOp):
            # Boolean operation (and, or)
            if isinstance(node.op, ast.And):
                return all(self._evaluate_node(v, context) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._evaluate_node(v, context) for v in node.values)

        elif isinstance(node, ast.UnaryOp):
            # Unary operation (not)
            if isinstance(node.op, ast.Not):
                return not self._evaluate_node(node.operand, context)

        elif isinstance(node, ast.Compare):
            # Comparison operation
            left = self._evaluate_node(node.left, context)

            for op, right in zip(node.ops, node.comparators):
                right_val = self._evaluate_node(right, context)

                if isinstance(op, ast.Eq):
                    if not (left == right_val):
                        return False
                elif isinstance(op, ast.NotEq):
                    if not (left != right_val):
                        return False
                elif isinstance(op, ast.Lt):
                    if not (left < right_val):
                        return False
                elif isinstance(op, ast.LtE):
                    if not (left <= right_val):
                        return False
                elif isinstance(op, ast.Gt):
                    if not (left > right_val):
                        return False
                elif isinstance(op, ast.GtE):
                    if not (left >= right_val):
                        return False

                left = right_val

            return True

        elif isinstance(node, ast.Call):
            # Function call (e.g., _ctx_get)
            if isinstance(node.func, ast.Name) and node.func.id == "_ctx_get":
                # Get path from context
                if node.args:
                    path = self._evaluate_node(node.args[0], context)
                    return self._get_nested_value(context, path)

        elif isinstance(node, ast.Constant):
            # Constant value (Python 3.8+)
            return node.value

        elif isinstance(node, ast.Num):
            # Number (Python 3.7)
            return node.n

        elif isinstance(node, ast.Str):
            # String (Python 3.7)
            return node.s

        elif isinstance(node, ast.NameConstant):
            # Boolean/None (Python 3.7)
            return node.value

        elif isinstance(node, ast.Name):
            # Variable name
            if node.id in ("True", "False", "None"):
                return ast.literal_eval(node.id)
            # Unknown variable, return as-is
            return node.id

        raise ValueError(f"Unsupported AST node type: {type(node)}")

    def _get_nested_value(self, context: dict[str, Any], path: str) -> Any:
        """
        Get nested value from context using dot notation path.

        Args:
            context: Context dictionary
            path: Dot-separated path (e.g., "user.profile.age")

        Returns:
            Value at path

        Raises:
            KeyError: If path doesn't exist
        """
        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value[part]
            else:
                value = getattr(value, part)

        return value


def parse_filter(expression: str) -> callable:
    """
    Convenience function to parse filter expression.

    Args:
        expression: DSL filter expression

    Returns:
        Filter function

    Example:
        >>> filter_func = parse_filter("user.age >= 18")
        >>> filter_func({"user": {"age": 25}})
        True
    """
    dsl = FilterDSL()
    return dsl.parse(expression)
