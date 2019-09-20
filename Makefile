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

submodules:  # create conda testing environment
	git submodule init && git submodule update

lint:  # check style with flake8
	source activate amigos && flake8

test: lint  # run unit tests
	source activate amigos && pytest --ignore amigos/ext

install: env submodules # install the environment and local source
	python setup.py develop

deploy: install-ssh-key # sync the code to the amigos box
	scp -prCB codes root@amigos:/media/mmcblk0p1

serial: # Connect to triton serial console
	picocom -b 115200 /dev/ttyUSB0

install-ssh-key:
	cat ~/.ssh/id_rsa_amigos.pub | ssh root@amigos "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
