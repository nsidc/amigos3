.PHONY: clean clean-pyc clean-build help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

env:  # create conda testing environment
	conda env create -f environment.yml

lint:  # check style with flake8
	source activate amigos && flake8

test: lint  # run tests quickly with the default Python
	source activate amigos && pytest

install: env  # install the environment and local source
	python setup.py develop
