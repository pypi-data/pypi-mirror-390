set -euox pipefail

ruff format .

ruff check --fix .

mypy --install-types --non-interactive src/charlie

pytest -v --tb=short
