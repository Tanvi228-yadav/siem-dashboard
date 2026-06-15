# Makefile for SIEM Dashboard project

.PHONY: install test lint up down app generate alerts shell

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

lint:
	flake8 .

test:
	pytest -q

up:
	docker-compose up -d

down:
	docker-compose down

app:
	python app.py

generate:
	python scripts/generate_logs.py

alerts:
	python scripts/alerts.py

shell:
	python
