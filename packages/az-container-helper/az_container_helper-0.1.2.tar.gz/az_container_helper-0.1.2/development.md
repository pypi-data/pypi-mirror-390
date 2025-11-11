## Development

### Setup project
The project needs `uv` for package management. To install on e.g. Mac OS X do

    $ brew install uv

Then you can initialize the project

    $ uv sync

### Run linter and tests

    $ uv run ruff check
    $ uv run pytest -s

### Teardown project

    $ rm -r .venv uv.lock

### Upload to PyPi
Before you can upload packages to PyPi you need to create an account at PyPi, activate 2FA (e.g. use Ente Authenticator)
and create an API-Token. Then you can configure `uv` to use the API-Token like

    $ uv auth login upload.pypi.org
    username: __token__
    password: <your-api-token>

You can then build and upload the package to PyPi simply by

    $ uv build                         # will build both sdist and wheel 
    $ uv publish --username __token__  # by default publishes to PyPi

To test if your package was successfully published you can do

    $ uv run --with "az-utils==<your-version>" --no-project -- python -c "import az_utils"
