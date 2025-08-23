from __future__ import annotations

import ast
import typing
from importlib.metadata import version

RUF010 = "RUF010 Use explicit conversion flag"
RUF018 = "RUF018 Avoid assignment expressions in assert statements"
RUF020 = "RUF020 {} | T is equivalent to T"
RUF025 = "RUF025 Unnecessary dict comprehension for iterable; use dict.fromkeys instead"


def _is_typing_object(
    node: ast.AST,
    name: str,
) -> bool:
    return (isinstance(node, ast.Name) and node.id == name) or (
        isinstance(node, ast.Attribute)
        and node.attr == name
        and isinstance(node.value, ast.Name)
        and node.value.id in {"typing", "typing_extensions"}
    )


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

    def visit_FormattedValue(self, node: ast.FormattedValue) -> None:
        if (
            node.conversion == -1
            and isinstance(node.value, ast.Call)
            and not node.value.keywords
            and len(node.value.args) == 1
            and not isinstance(
                node.value.args[0], (ast.Dict, ast.DictComp, ast.Set, ast.SetComp)
            )
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in {"ascii", "repr", "str"}
        ):
            # On 3.12, the node position matches the actual curly braces rather than
            # the start of the f-string.
            self.errors.append(
                (
                    node.lineno,
                    node.col_offset,
                    RUF010,
                )
            )

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
            self.errors.append(
                (
                    node.lineno,
                    node.col_offset,
                    RUF025,
                )
            )

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, ast.BitOr):
            for never_like in "Never", "NoReturn":
                for side in node.left, node.right:
                    if _is_typing_object(side, never_like):
                        self.errors.append(
                            (
                                node.lineno,
                                side.col_offset,
                                RUF020.format(never_like),
                            )
                        )
            if isinstance(node.left, ast.BinOp):
                self.visit_BinOp(node.left)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if _is_typing_object(node.value, "Union") and isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                for never_like in "Never", "NoReturn":
                    if _is_typing_object(elt, never_like):
                        self.errors.append(
                            (
                                node.lineno,
                                elt.col_offset,
                                RUF020.format(never_like),
                            )
                        )

    def visit_Assert(self, node: ast.Assert) -> None:
        if isinstance(node.test, ast.NamedExpr):
            self.errors.append(
                (
                    node.lineno,
                    node.col_offset,
                    RUF018,
                )
            )


class Plugin:
    name = "flake8-ruff"
    version = version("flake8-ruff")

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
