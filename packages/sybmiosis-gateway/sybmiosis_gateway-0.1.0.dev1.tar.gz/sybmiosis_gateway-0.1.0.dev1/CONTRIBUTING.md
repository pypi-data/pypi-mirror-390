# Contribution guide

Welcome to the Symbiosis project and thanks for contributing to our project!
We've made this guide to help you setting up your development environment and
contributing changes with as little fuss as possible. We value speed and
iteration. The information here should help you get there faster!

We cover the following topics in this guide:

- [Preparing your environment](#preparing-your-environment)
- [Making changes](#making-changes)
- [Committing changes](#committing-changes)

Let's get you started.

## :computer: Preparing your environment

Before you can start working on the code, make sure you have the prerequisites
available on your machine. Then follow these steps to configure your development
environment.

### Prerequisites

- [UV](https://astral.sh/uv)
- [Visual Studio Code](https://code.visualstudio.com)
- [Docker](https://www.docker.com/) or [Podman](https://podman.io/)

### Step 1: Clone the repository to disk

Use the following command to clone the repository:

```bash
git clone https://github.com/wmeints/symbiosis
```

### Step 2: Install pre-commit hooks

This project uses [pre-commit](https://pre-commit.com/) to run scripts before
committing changes to GIT. This helps us prevent common mistakes when making
changes in the project.

To install the tool use the following command:

```bash
uv tool install pre-commit
```

After install the pre-commit tool, run the following command from the
`sybmiosis` project directory to setup the pre-commit hooks in the repository:

```bash
pre-commit install
```

### Step 3: Synchronize the dependencies

Run the following command to synchronize the project dependencies:

```bash
uv sync
```

## :wrench: Making changes

Please use Pull Requests to submit changes in the project! We use PR builds
to verify changes before updating the main branch. We want our main branch
to be publishable as much as posisble.

You are welcome to submit multiple commits in one PR. In fact, we recommend it.
The easier it is to read the commit messages, the better :-)

We have a few common tasks that help you maintain the code without too much
fuss. The order in which you run these commands doesn't really matter.

### Verifying code quality

Use the following command to quickly check and fix common code quality issues.

```bash
uv run ruff check --fix
```

### Running tests

You can run unit-tests with the following command:

```bash
uv run pytest
```

## :ship: Committing changes

We use conventional commits so we can generate release notes automatically without
human intervention. We have a pre-commit hook to help you follow the standard so
this should be fairly easy to follow.

We have a few rules for commit messages:

- Use `feat: <description>` when committing a new feature to the application.
- Use `fix: <description>` when fixing a bug in the code.
- Use `chore: <description>` when performing build maintenance.
- Use `docs: <description>` when writing docs.

Keep descriptions short and use the extended commit message description to provide
additional information on what you created or changed.

For example:

```text
feat: add support for OpenAI models

The application now includes provider support for communicating with OpenAI
models. Users can configure OpenAI models via the API and use them via the
universal API interface.

Closes #23
```

Use the final line in your commit message for closing issues.

You can learn more about conventional commits
[on their website](https://www.conventionalcommits.org/en/v1.0.0/#summary).