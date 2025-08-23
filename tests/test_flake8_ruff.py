from __future__ import annotations

import ast
import sys
import textwrap

from flake8_ruff import Plugin


def run(source: str) -> list[tuple[int, int, str]]:
    tree = ast.parse(textwrap.dedent(source))
    return [(line, col, msg) for (line, col, msg, type_) in Plugin(tree).run()]


def test_ruf010_ascii() -> None:
    src = """\
    f"abc {ascii(bar)} xyz"
    """
    expected = [(1, 6, "RUF010 Use explicit conversion flag")]
    if sys.version_info >= (3, 12):
        assert expected == run(src)
    else:
        assert expected[0][2] == run(src)[0][2]


def test_ruf010_repr() -> None:
    src = """\
    f"abc {repr(123)} xyz"
    """
    expected = [(1, 6, "RUF010 Use explicit conversion flag")]
    if sys.version_info >= (3, 12):
        assert expected == run(src)
    else:
        assert expected[0][2] == run(src)[0][2]


def test_ruf010_str() -> None:
    src = """\
    f"abc {(str(123))} xyz"
    """
    expected = [(1, 6, "RUF010 Use explicit conversion flag")]
    if sys.version_info >= (3, 12):
        assert expected == run(src)
    else:
        assert expected[0][2] == run(src)[0][2]


def test_ruf010_set() -> None:
    src = """\
    f"abc {str({})} xyz"
    """
    expected: list[tuple[int, int, str]] = []
    assert expected == run(src)


def test_ruf010_dict() -> None:
    src = """\
    f"abc {str({k: v for k, v in enumerate(foo)})} xyz"
    """
    expected: list[tuple[int, int, str]] = []
    assert expected == run(src)


def test_ruf018() -> None:
    src = """\
    assert (x := 1), "message"
    """
    expected = [(1, 0, "RUF018 Avoid assignment expressions in assert statements")]
    assert expected == run(src)


def test_ruf018_no_assign() -> None:
    src = """\
    assert x == 1, "message"
    """
    expected: list[tuple[int, int, str]] = []
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


def test_ruf020_no_return_invalid_op() -> None:
    src = """\
    from typing import NoReturn
    foo: None & NoReturn
    """
    expected: list[tuple[int, int, str]] = []
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


def test_ruf020_union_no_subscript() -> None:
    src = """\
    from typing import NoReturn
    def foo() -> tuple[str, int, NoReturn]: ...
    """
    expected: list[tuple[int, int, str]] = []
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
