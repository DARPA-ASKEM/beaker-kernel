SHELL=/usr/bin/env bash
BASEDIR = $(shell pwd)
COMPOSE_ARGS=--file docker/docker-compose.yml

.PHONY:build
build:
	docker build --file docker/Dockerfile.beaker -t beaker-kernel:latest .

.PHONY:fresh-build
fresh-build:
	docker build --file docker/Dockerfile.beaker -t beaker-kernel:latest --no-cache .

.PHONY:inspect
inspect:
	docker compose ${COMPOSE_ARGS} exec jupyter /bin/bash

.PHONY:down
down:
	docker compose ${COMPOSE_ARGS} down

.PHONY:start # called `start` instead of `up` because it does more than `docker compose up`
start:
	docker compose ${COMPOSE_ARGS} pull;
	docker compose ${COMPOSE_ARGS} up -d --build --remove-orphans;
	docker compose ${COMPOSE_ARGS} logs -f jupyter || true;

.PHONY:logs
logs:
	docker compose ${COMPOSE_ARGS} logs -f jupyter || true;

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

