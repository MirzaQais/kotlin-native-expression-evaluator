"""Restricted Kotlin-like expression evaluator used by the Phase-1 PoC."""

from __future__ import annotations
import ast
import re
from typing import Any, Mapping


class KExprError(RuntimeError):
    pass


def kotlin_to_python(expr: str) -> str:
    expr = expr.replace("&&", " and ").replace("||", " or ")
    expr = re.sub(r"(?<![=!<>])!(?!=)", " not ", expr)
    expr = re.sub(r"\btrue\b", "True", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bfalse\b", "False", expr, flags=re.IGNORECASE)
    return expr.strip()


_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
}

_UNARYOPS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
    ast.Not: lambda a: not a,
}

_CMPOPS = {
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}


class SafeKotlinEvaluator:
    def __init__(self, variables: Mapping[str, Any]):
        self.variables = dict(variables)

    def evaluate(self, expression: str) -> Any:
        try:
            tree = ast.parse(kotlin_to_python(expression), mode="eval")
        except SyntaxError as exc:
            raise KExprError(f"Invalid expression: {exc.msg}") from exc
        return self._visit(tree.body)

    def _visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, bool)):
                return node.value
            raise KExprError("Only numeric and Boolean literals are supported")

        if isinstance(node, ast.Name):
            if node.id not in self.variables:
                raise KExprError(f"Unknown or unsupported variable: {node.id}")
            value = self.variables[node.id]
            if not isinstance(value, (int, float, bool)):
                raise KExprError(f"Unsupported value type for variable: {node.id}")
            return value

        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](self._visit(node.left), self._visit(node.right))

        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
            return _UNARYOPS[type(node.op)](self._visit(node.operand))

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for value in node.values:
                    if not bool(self._visit(value)):
                        return False
                return True
            if isinstance(node.op, ast.Or):
                for value in node.values:
                    if bool(self._visit(value)):
                        return True
                return False

        if isinstance(node, ast.Compare):
            left = self._visit(node.left)
            for op, rhs_node in zip(node.ops, node.comparators):
                fn = _CMPOPS.get(type(op))
                if fn is None:
                    raise KExprError(f"Unsupported comparison: {type(op).__name__}")
                right = self._visit(rhs_node)
                if not fn(left, right):
                    return False
                left = right
            return True

        raise KExprError(f"Unsupported expression construct: {type(node).__name__}")
