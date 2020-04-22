all	: Dockerfile jupyter_notebook_config.py
	docker build -t nijhawanlab/tools:0.1 .
