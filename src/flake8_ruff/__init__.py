from __future__ import annotations

import ast
import typing

RUF020 = "RUF020 {} | T is equivalent to T"
RUF025 = "RUF025 Unnecessary dict comprehension for iterable; use dict.fromkeys instead"


def _is_typing_object(
    node: ast.AST,
    name: str,
) -> bool:
    if isinstance(node, ast.Name) and node.id == name:
        return True
    if (
        isinstance(node, ast.Attribute)
        and node.attr == name
        and isinstance(node.value, ast.Name)
        and node.value.id in {"typing", "typing_extensions"}
    ):
        return True
    return False


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[tuple[int, int, str]] = []
        self._logging_name: str | None = None
        self._logger_name: str | None = None
        self._from_imports: dict[str, str] = {}
        self._stack: list[ast.AST] = []

    def visit(self, node: ast.AST) -> None:
        self._stack.append(node)
        super().visit(node)
        self._stack.pop()

    def visit_DictComp(self, node: ast.DictComp) -> None:
        if (
            len(node.generators) == 1
            and not node.generators[0].ifs
            and not node.generators[0].is_async
            and isinstance(node.key, ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.generators[0].target, ast.Name)
            and node.key.id == node.generators[0].target.id
        ):
            self.errors.append((
                node.lineno,
                node.col_offset,
                RUF025,
            ))

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, ast.BitOr):
            for never_like in "Never", "NoReturn":
                for side in node.left, node.right:
                    if _is_typing_object(side, never_like):
                        self.errors.append((
                            node.lineno,
                            side.col_offset,
                            RUF020.format(never_like),
                        ))
            if isinstance(node.left, ast.BinOp):
                self.visit_BinOp(node.left)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if _is_typing_object(node.value, "Union") and isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                for never_like in "Never", "NoReturn":
                    if _is_typing_object(elt, never_like):
                        self.errors.append((
                            node.lineno,
                            elt.col_offset,
                            RUF020.format(never_like),
                        ))


class Plugin:
    name = "flake8-ruff"

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(
        self,
    ) -> typing.Generator[tuple[int, int, str, type[typing.Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        type_ = type(self)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type_
