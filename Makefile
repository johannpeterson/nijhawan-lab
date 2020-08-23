include .env

all	: Dockerfile docker/jupyter_notebook_config.py
	env $(cat .env | grep -v "#" | xargs)
	docker build -t $(DOCKER_IMAGE) .
