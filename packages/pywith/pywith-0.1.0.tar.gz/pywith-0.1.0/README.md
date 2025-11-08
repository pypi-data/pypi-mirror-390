# pywith

Launch [ptpython](https://github.com/prompt-toolkit/ptpython) with custom PyPI packages, with [uv](https://github.com/astral-sh/uv)'s help.

Useful for trying out libraries or when we use them rarely.

## Installation

```bash
uv tool install pywith
```

## Usage

```bash
pywith <package> [<package> ...]
```

## Example

```bash
pywith requests pandas numpy
```
