# Releasing to PyPI

This project uses a modern PEP 621 `pyproject.toml` with the Hatchling build backend. Below are the steps to build and publish to PyPI using uv-ship.

## Prereqs

- Python 3.11+
- `uv` installed (https://github.com/astral-sh/uv)
- `uv-ship` installed (via `uv tool install uv-ship`)
- PyPI accounts and API tokens for TestPyPI and/or PyPI

## Run tests and lint

- `uv run pytest`
- Optionally: `uv run nox`

## Releasing

- `uv-ship next <type>` where type is major|minor|patch
- Follow the prompts and release the new version to Github
- `rm -rf dist`
- `uv build`
- `uvx twine upload dist/*`
