# Symbiosis Gateway

Symbiosis Gateway is an open-source AI gateway written in Python. The goal of
this project is to build a centralized system to connect large language models
and image generation models to applications.

## Used technology

- [Python 3.13](https://www.python.org/downloads/) - The main programming language for the AI gateway
- [UV](https://github.com/astral-sh/uv) - Manages dependencies, building packages, and the python virtual environment for the project
- [Postgres](https://www.postgresql.org/) - For storing configuration data in the gateway
- [FastAPI](https://fastapi.tiangolo.com/) - For building the REST interface of the application
- [SQLModel](https://sqlmodel.tiangolo.com/) - For interacting with the postgres database from the application
- [Typer](https://typer.tiangolo.com/) - For the CLI interface of the application
- [Pytest](https://docs.pytest.org/en/stable/) - For running unit-tests in the application
- [Ruff](https://astral.sh/ruff) - Linter and formatter used to verify and format the code for both the main application and the tests

## Project structure 

- `docs/architecture` - Contains the architecture documentation following the arc42 standard
- `docs/product` - Contains the product documentation for the application describing requirements and decisions related to product features
- `src/symbiosis` - Contains the main application code written in Python
- `tests` - Contains the unit-tests written in pytest for the main application

## Important quality measures

- Always run unit-tests with `uv run pytest` after you've implemented changes in the main application or the tests
- Always run the linter with `uv run ruff check --fix` after you've implemented changes in the main application or tests

## Committing changes to GIT

- Use conventional commit messages when committing changes
- Commit relevant changes together in one commit

## Building the package

- Use `uv build` to build packages locally. Note: This produces a package without versioning, we only publish packages through the github workflow. 