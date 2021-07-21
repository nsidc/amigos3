.PHONY: env submodules clean lint test serial-con ssh-con sync backup
.DEFAULT_GOAL := help

SHELL=/bin/bash

# --------------------------------------------------------------------------------
# Development
# --------------------------------------------------------------------------------

env:  # create conda testing environment
	conda env list | grep amigos-test-env || \
	    conda env create -f environment.yml

submodules:  # create conda testing environment
	git submodule init && git submodule update

install-dev: env submodules # install the environment and local source
	source activate amigos-test-env && \
	    python setup.py develop

clean:
	find . -name '*.pyc' -delete

lint:  # check style with flake8
	source activate amigos-test-env && \
	    flake8 --ignore E203 --exclude ./honcho/ext,./backup,./build

test: clean lint  # run unit tests
	source activate amigos-test-env && \
	    PYTHONPATH="$$PYTHONPATH:./honcho/ext" \
	    pytest --ignore ./honcho/ext --ignore ./backup --ignore ./build --cov ./

codecov:
	source activate amigos-test-env && \
	    codecov

# --------------------------------------------------------------------------------
# Communication
# --------------------------------------------------------------------------------

serial-con: # Connect to triton serial console
	sudo picocom -b 115200 /dev/ttyUSB0

ssh-con: # Connect to triton over ssh
	ssh root@amigos

# --------------------------------------------------------------------------------
# Deployment
# --------------------------------------------------------------------------------

sync: sync-system sync-code

sync-system:
	ssh root@amigos "mount / -o remount,rw"
	rsync -vlrEc system/ root@amigos:/
	ssh root@amigos "mount / -o remount,ro"

sync-code: clean # sync the code to the amigos box
	mkdir -p build
	rm -rf build/*
	cp -pr honcho build/
	find ./build | grep .git | xargs rm -rf
	rsync -vlrEc build/honcho root@amigos:/media/mmcblk0p1

# --------------------------------------------------------------------------------
# Deployment
# --------------------------------------------------------------------------------

pull-data: # sync the amigos box sd card
	mkdir -p ./data
	scp -prCB root@amigos:/media/mmcblk0p1/data "./data/$$(date +%F_%R)"

backup: # sync the amigos box sd card
	mkdir -p ./backup
	scp -prCB root@amigos:/media/mmcblk0p1 "./backup/$$(date +%F_%R)"
