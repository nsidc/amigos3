.PHONY: env submodules lint test install deploy seril install-ssh-key help
.DEFAULT_GOAL := help

SHELL=/bin/bash

env:  # create conda testing environment
	conda env create -f environment.yml

submodules:  # create conda testing environment
	git submodule init && git submodule update

lint:  # check style with flake8
	source activate amigos-test-env && flake8 --exclude ./codes/ext,./codes/python/argparse.py

test: lint  # run unit tests
	source activate amigos-test-env && pytest --ignore ./codes/ext

install: env submodules # install the environment and local source
	python setup.py develop

deploy: install-ssh-key # sync the code to the amigos box
	scp -prCB codes root@amigos:/media/mmcblk0p1

serial: # Connect to triton serial console
	picocom -b 115200 /dev/ttyUSB0

install-ssh-key:
	cat ~/.ssh/id_rsa_amigos.pub | ssh root@amigos "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
