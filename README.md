# flake8-ruff

A Flake8 plugin that implements miscellaneous checks from [Ruff](https://github.com/astral-sh/ruff).

Specifically, this plugin implements checks that are under the `RUF` category
(the rules that do not have a direct equivalent in Flake8).

## Requirements

Python 3.9 to 3.12 is supported.

## Installation

Install from PyPI. For example,

```bash
pip install flake8-ruff
```

Then follow the instructions on the [Flake8 documentation](https://flake8.pycqa.org/en/latest/index.html)
to enable the plugin.

## Checks

### RUF018 Avoid assignment expressions in `assert` statements

Checks for named assignment expressions in `assert` statements. When Python is
run with the `-O` option, the `assert` statement is ignored, and the assignment
expression is not executed. This can lead to unexpected behavior.

For example, replace

```python
assert (result := foo()) is not None
```

with

```python
result = foo()
assert result is not None
```

### RUF020 `typing.Never | T` is equivalent to `T`

Checks for `typing.Never` and `typing.NoReturn` in union types, which is
redundant.

For example, replace

```python
typing.Never | int | None
```

with

```python
int | None
```

Derived from [never-union (RUF020)](https://docs.astral.sh/ruff/rules/never-union/).

### RUF025 Unnecessary dict comprehension for iterable; use `dict.fromkeys` instead

Checks for dict comprehensions that create a dictionary from an iterable with a
constant value. Instead, use `dict.fromkeys`, which is more efficient.

For example, replace

```python
{key: 0 for key in keys}
```

with

```python
dict.fromkeys(keys, 0)
```

and

```python
{key: None for key in keys}
```

with

```python
dict.fromkeys(keys)
```

Derived from [unnecessary-dict-comprehension-for-iterable (RUF025)](https://docs.astral.sh/ruff/rules/unnecessary-dict-comprehension-for-iterable/).
