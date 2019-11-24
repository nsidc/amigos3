.PHONY: env submodules clean lint test serial-con install-ssh-key ssh-con
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
	    flake8 --exclude ./honcho/ext,./backup,./build

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

install-ssh-key:
	ssh root@amigos "mount / -o remount,rw"
	cat ~/.ssh/id_rsa_amigos.pub | ssh root@amigos "mkdir -p ~/.ssh && cat > ~/.ssh/authorized_keys"
	ssh root@amigos "mount / -o remount,ro"

ssh-con: # Connect to triton over ssh
	ssh root@amigos

# --------------------------------------------------------------------------------
# Deployment
# --------------------------------------------------------------------------------

install-win-ssh-key:
	ssh root@amigos "mount / -o remount,rw"
	# TODO
	ssh root@amigos "mount / -o remount,ro"

install-hosts:
	ssh root@amigos "mount / -o remount,rw"
	scp -pCB system/hosts root@amigos:/etc/hosts
	ssh root@amigos "mount / -o remount,ro"

sync-code: clean # sync the code to the amigos box
	mkdir -p build
	rm -rf build/*
	cp -pr honcho build/
	find ./build | grep .git | xargs rm -rf
	ssh root@amigos "rm -rf /media/mmcblk0p1/*"
	scp -prCB build/honcho root@amigos:/media/mmcblk0p1

setup-login-shell: install-ssh-key 
	ssh root@amigos "mount / -o remount,rw"
	# Set bash shell for root
	ssh root@amigos "sed -i 's/root:x:0:0:root:\/root:\/bin\/sh/root:x:0:0:root:\/root:\/bin\/bash/g' /etc/passwd"
	# Install bashrc
	scp -pCB system/.bashrc root@amigos:/root
	ssh root@amigos "mount / -o remount,ro"

# --------------------------------------------------------------------------------
# Deployment
# --------------------------------------------------------------------------------

backup: # sync the amigos box sd card
	mkdir -p ./backup
	scp -prCB root@amigos:/media/mmcblk0p1 "./backup/$$(date +%F_%R)"
