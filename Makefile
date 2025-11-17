.PHONY: venv install ingest run test clean help

help:
	@echo "Pokemon Data Agent - Makefile Commands"
	@echo "======================================="
	@echo "make venv      - Create virtual environment"
	@echo "make install   - Install dependencies"
	@echo "make ingest    - Ingest Pokemon data from PokeAPI"
	@echo "make run       - Start the FastAPI server"
	@echo "make test      - Run all tests"
	@echo "make clean     - Clean cache and database"

venv:
	python -m venv venv

install:
	pip install -r requirements.txt

ingest:
	python -m app.ingest --limit 251

run:
	python pokemon_os.py

run-api:
	uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

run-os:
	uvicorn pokemon_os:app --host 0.0.0.0 --port 7777 --reload

test:
	pytest tests/ -v

clean:
	if exist cache rmdir /s /q cache
	if exist artifacts rmdir /s /q artifacts
	if exist pokemon.db del /f pokemon.db
	if exist .pytest_cache rmdir /s /q .pytest_cache
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
