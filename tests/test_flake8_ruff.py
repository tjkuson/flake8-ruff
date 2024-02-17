from __future__ import annotations

import ast
import textwrap

from flake8_ruff import Plugin


def run(source: str) -> list[tuple[int, int, str]]:
    tree = ast.parse(textwrap.dedent(source))
    return [(line, col, msg) for (line, col, msg, type_) in Plugin(tree).run()]


def test_ruf018() -> None:
    src = """\
    assert (x := 1), "message"
    """
    expected = [(1, 0, "RUF018 Avoid assignment expressions in assert statements")]
    assert expected == run(src)


def test_ruf020_never() -> None:
    src = """\
    from typing import Never
    foo: Never | None
    """
    expected = [(2, 5, "RUF020 Never | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_typing_never() -> None:
    src = """\
    import typing
    foo: None | typing.Never
    """
    expected = [(2, 12, "RUF020 Never | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_typing_extensions_never() -> None:
    src = """\
    import typing_extensions
    foo: None | typing_extensions.Never
    """
    expected = [(2, 12, "RUF020 Never | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_no_return() -> None:
    src = """\
    from typing import NoReturn
    foo: None | NoReturn
    """
    expected = [(2, 12, "RUF020 NoReturn | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_typing_no_return() -> None:
    src = """\
    import typing
    foo: typing.NoReturn | None | str
    """
    expected = [(2, 5, "RUF020 NoReturn | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_typing_extensions_no_return() -> None:
    src = """\
    import typing_extensions
    foo: typing_extensions.NoReturn | None
    """
    expected = [(2, 5, "RUF020 NoReturn | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_typing_union_never() -> None:
    src = """\
    import typing
    foo: typing.Union[typing.Never, None]
    """
    expected = [(2, 18, "RUF020 Never | T is equivalent to T")]
    assert expected == run(src)


def test_ruf020_union_no_return() -> None:
    src = """\
    from typing import Union, NoReturn
    def foo() -> Union[str, int, NoReturn]: ...
    """
    expected = [(2, 29, "RUF020 NoReturn | T is equivalent to T")]
    assert expected == run(src)


def test_ruf025_none_value() -> None:
    src = """\
    {k: None for k in range(10)}
    """
    expected = [
        (
            1,
            0,
            "RUF025 Unnecessary dict comprehension for iterable; use dict.fromkeys instead",
        ),
    ]
    assert expected == run(src)


def test_ruf025_str_value() -> None:
    src = """\
    {k: "v" for k in range(10)}
    """
    expected = [
        (
            1,
            0,
            "RUF025 Unnecessary dict comprehension for iterable; use dict.fromkeys instead",
        ),
    ]
    assert expected == run(src)


def test_ruf025_int_value() -> None:
    src = """\
    {k: 0 for k in range(10)}
    """
    expected = [
        (
            1,
            0,
            "RUF025 Unnecessary dict comprehension for iterable; use dict.fromkeys instead",
        ),
    ]
    assert expected == run(src)


def test_ruf025_list_value() -> None:
    src = """\
    {k: [] for k in range(10)}
    """
    expected: list[tuple[int, int, str]] = []
    assert expected == run(src)
