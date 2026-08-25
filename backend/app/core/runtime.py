from __future__ import annotations

import ast
import operator
from copy import deepcopy
from typing import Any

from .uam import NodeKind, UAMProcess


class SafeExpression:
    OPS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.And: lambda a, b: bool(a and b),
        ast.Or: lambda a, b: bool(a or b),
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    @classmethod
    def eval(cls, expression: str, context: dict[str, Any]) -> Any:
        tree = ast.parse(expression, mode="eval")
        return cls._eval(tree.body, context)

    @classmethod
    def _eval(cls, node: ast.AST, context: dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in context:
                raise KeyError(node.id)
            return context[node.id]
        if isinstance(node, ast.Attribute):
            value = cls._eval(node.value, context)
            if isinstance(value, dict):
                return value[node.attr]
            raise ValueError("attribute access is allowed only on dictionaries")
        if isinstance(node, ast.Subscript):
            return cls._eval(node.value, context)[cls._eval(node.slice, context)]
        if isinstance(node, ast.Compare):
            left = cls._eval(node.left, context)
            for op, comp in zip(node.ops, node.comparators):
                right = cls._eval(comp, context)
                fn = cls.OPS.get(type(op))
                if not fn or not fn(left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            values = [cls._eval(v, context) for v in node.values]
            fn = cls.OPS[type(node.op)]
            result = values[0]
            for value in values[1:]:
                result = fn(result, value)
            return result
        if isinstance(node, ast.BinOp):
            fn = cls.OPS.get(type(node.op))
            if not fn:
                raise ValueError("operator not allowed")
            return fn(cls._eval(node.left, context), cls._eval(node.right, context))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not cls._eval(node.operand, context)
        if isinstance(node, ast.List):
            return [cls._eval(x, context) for x in node.elts]
        if isinstance(node, ast.Dict):
            return {cls._eval(k, context): cls._eval(v, context) for k, v in zip(node.keys, node.values)}
        raise ValueError(f"unsafe or unsupported expression: {type(node).__name__}")


class UAMRuntime:
    """Deterministic UAM interpreter used for ProofRun simulation.

    It intentionally does not execute vendor code. Side-effecting nodes use declared simulation
    behavior from node.config, which makes replay safe and deterministic.
    """

    def execute(self, process: UAMProcess, input_data: dict[str, Any]) -> dict[str, Any]:
        state: dict[str, Any] = {
            "input": deepcopy(input_data),
            "output": {},
            "vars": deepcopy(process.variables),
            "trace": [],
        }
        starts = [n for n in process.nodes if n.kind == NodeKind.START]
        if not starts:
            raise ValueError("process has no start node")
        current = starts[0]
        visited = 0

        while current.kind != NodeKind.END:
            visited += 1
            if visited > 10_000:
                raise RuntimeError("execution exceeded safe step limit")
            state["trace"].append({"node_id": current.id, "name": current.name, "kind": current.kind.value})
            self._apply_node(current, state)
            outgoing = process.outgoing(current.id)
            if not outgoing:
                break
            edge = self._select_edge(outgoing, state)
            current = process.node(edge.target)

        if current.kind == NodeKind.END:
            state["trace"].append({"node_id": current.id, "name": current.name, "kind": current.kind.value})
        return state

    def _select_edge(self, edges, state):
        unconditional = []
        for edge in edges:
            if not edge.condition:
                unconditional.append(edge)
                continue
            try:
                if SafeExpression.eval(edge.condition, state):
                    return edge
            except Exception:
                continue
        if unconditional:
            return unconditional[0]
        raise RuntimeError("no outgoing edge condition matched")

    def _apply_node(self, node, state):
        config = node.config or {}
        if "set_output" in config:
            for key, expression in config["set_output"].items():
                state["output"][key] = self._resolve(expression, state)
        if "set_var" in config:
            for key, expression in config["set_var"].items():
                state["vars"][key] = self._resolve(expression, state)
        if node.kind == NodeKind.DECISION and config.get("expression"):
            state["vars"][f"decision:{node.id}"] = bool(SafeExpression.eval(config["expression"], state))

    @staticmethod
    def _resolve(value, state):
        if isinstance(value, str) and value.startswith("="):
            return SafeExpression.eval(value[1:], state)
        return deepcopy(value)
