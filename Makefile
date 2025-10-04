.PHONY: run test fmt lint typecheck
run: ; uvicorn app.main:app --reload
test: ; pytest -q
fmt: ; ruff check --fix . && ruff format .
lint: ; ruff check .
