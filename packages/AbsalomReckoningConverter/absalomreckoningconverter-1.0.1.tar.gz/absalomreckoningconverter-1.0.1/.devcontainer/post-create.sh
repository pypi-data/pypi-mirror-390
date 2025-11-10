pipx install poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.prompt '.venv'
poetry install
poetry shell