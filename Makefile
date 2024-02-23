SHELL=/usr/bin/env bash
BASEDIR = $(shell pwd)
COMPOSE_ARGS=--file docker/docker-compose.yml

.PHONY:build
build:
	docker build --file Docker.beaker . -t beaker-kernel:latest

.PHONY:dev
dev:
	if [[ "$$(docker compose ps | grep 'jupyter')" == "" ]]; then \
		docker compose ${COMPOSE_ARGS} pull; \
		docker compose ${COMPOSE_ARGS} up -d --build && \
		(sleep 1; python -m webbrowser "http://localhost:8888"); \
		docker compose ${COMPOSE_ARGS} logs -f jupyter || true; \
	else \
		docker compose ${COMPOSE_ARGS} down jupyter && \
		docker compose ${COMPOSE_ARGS} up -d jupyter && \
		(sleep 1; python -m webbrowser "http://localhost:8888"); \
		docker compose ${COMPOSE_ARGS} logs -f jupyter || true; \
	fi


.env:
	@if [[ ! -e ./.env ]]; then \
		cp env.example .env; \
		echo "Don't forget to set your OPENAI key in the .env file!"; \
	fi

