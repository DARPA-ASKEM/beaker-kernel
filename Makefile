SHELL=/bin/bash
BASEDIR = $(shell pwd)

.PHONY:build
build:
	docker build . -t beaker-kernel:latest

.PHONY:dev
dev:
	if [[ "$$(docker compose ps | grep 'jupyter')" == "" ]]; then \
		docker compose pull; \
		docker compose up -d --build && \
		(sleep 1; python -m webbrowser "http://localhost:8888/dev_ui"); \
		docker compose logs -f jupyter || true; \
	else \
		docker compose down jupyter && \
		docker compose up -d jupyter && \
		(sleep 1; python -m webbrowser "http://localhost:8888/dev_ui"); \
		docker compose logs -f jupyter || true; \
	fi


.env:
	@if [[ ! -e ./.env ]]; then \
		cp env.example .env; \
		echo "Don't forget to set your OPENAI key in the .env file!"; \
	fi
