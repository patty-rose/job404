.PHONY: build run

build:
	docker build -t interview-practice .

run:
	docker run --rm -it -v "$(PWD)/data:/app/data" interview-practice

.DEFAULT_GOAL := run
