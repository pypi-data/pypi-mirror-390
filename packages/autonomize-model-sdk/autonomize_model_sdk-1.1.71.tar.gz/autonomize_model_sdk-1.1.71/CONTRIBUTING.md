# Contributing

Here is a quickstart guide on how to contribute to the Autonomize Model SDK!

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/autonomize-ai/autonomize-model-sdk.git
    ```
2. Navigate to the project directory:
    ```bash
    cd autonomize-model-sdk
    ```
3. Create a virtual environment, we recommend [Miniconda](https://docs.anaconda.com/miniconda/) for environment management:
    ```bash
    conda create -n autonomize-dev python=3.12
    conda activate autonomize-dev
    ```
4. Install the required dependencies. We recommend [uv](https://github.com/astral-sh/uv) for package management:
    ```bash
    uv sync
    ```
5. Install the development dependencies. These dependencies are only required if you plan to contribute to this project:
    ```bash
    uv sync --all-extras
    pre-commit install
    ```

## Validating your changes

After making changes to source, make sure to run the pre-commit hooks as well as the linters and check the tests.

### Formatting the code

We use `black` autoformatter which is a PEP 8 compliant formatter. It reformats the non-compliant files *in-place*. The reformatted files needs to be added again in the git staging area.

```bash
make format
```

### Linting

We have various lints (pre-commit hooks, isort, autoflake, etc.) to run against the source code. This will also run the test cases.

```bash
make lint
```

### Testing

If you modified or added code logic, **create test(s)**, because they help preventing other maintainers from accidentally breaking the nice things you added / re-introducing the bugs you fixed.

- In almost all cases, add **unit tests**.
- If your change involves adding a new integration, also add **integration tests**.

Our tests are stored in the `tests` directory. We use the testing framework [pytest](https://docs.pytest.org/), so you can just run `pytest tests` to run all the tests.

### Creating an Example Notebook

For changes that involve entirely new features, it may be worth adding an example Jupyter notebook to showcase
this feature.

Example notebooks can be found in the `examples` directory of the repository.

### Creating a pull request

Directly pushing to the `main` branch is not preferred to prevent potential disruptions or issues in the codebase. To contribute safely and effectively, please follow these steps:

1. Create a Branch: In the repo, create a new branch for your feature or bug fix. Use a descriptive branch name that explains the purpose of your changes. For example: `feature/new-model-integration` or `fix/inference-pipeline`. These branch naming conventions are advised, but not strictly enforced.

2. Commit Your Changes: Make your changes in the new branch. Be sure to:
    - Write clear commit messages
    - Follow the existing coding standards and conventions
    - Ensure that your changes are well-tested and documented

3. Push the Changes: Push your branch to the remote repository and create a pull request.

## Code of Conduct

We are committed to fostering an open and welcoming environment. By participating in this project, you agree to:

- Be respectful and inclusive of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Questions or Need Help?

If you have questions or need help with the contribution process:

- Open an issue in the repository
- Check existing issues and pull requests for similar topics
- Review our documentation

Thank you for contributing to the Autonomize Model SDK!
