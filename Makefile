.PHONY: run test lint check

run:
	docker compose -f infra/compose/docker-compose.yml up --build

test:
	PYTHONPATH=backend pytest -q backend/tests

check:
	./scripts/local_check.sh
