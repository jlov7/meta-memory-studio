.PHONY: install install-hooks dev backend frontend check test e2e verify screenshots demo

install:
	cd backend && uv sync --group dev
	cd frontend && pnpm install

install-hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit
	@echo "Git hooks installed from .githooks/"

dev:
	@echo "Starting backend + frontend"
	$(MAKE) -j 2 backend frontend

backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && pnpm install && pnpm dev

check:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy .
	cd frontend && pnpm lint && pnpm typecheck

test:
	cd backend && uv run pytest -q
	cd frontend && pnpm test

e2e:
	cd frontend && pnpm exec playwright install --with-deps && pnpm e2e

verify: check test e2e

screenshots:
	./scripts/capture_readme_gallery.sh

demo:
	cd backend && uv run python ../scripts/import_demo.py --input ../examples/sample_traces
	@echo "Now open http://localhost:3000 and select the Demo workspace"
