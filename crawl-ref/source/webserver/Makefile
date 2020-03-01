lint:
	flake8 *.py


format:
	isort -rc .


install-deps:
	pip-sync requirements/base.txt


install-deps-dev:
	pip-sync requirements/dev.txt


sync-deps:
	pip-compile --output-file requirements/dev.txt requirements.in/dev.txt
	pip-compile --output-file requirements/base.txt requirements.in/base.txt
	pip-sync requirements/dev.txt


.PHONY: lint format install-deps-dev install-deps sync-deps
