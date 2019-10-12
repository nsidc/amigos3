.PHONY: env submodules lint test install deploy serial install-ssh-key help backup
.DEFAULT_GOAL := help

SHELL=/bin/bash

env:  # create conda testing environment
	conda env list | grep amigos-test-env || conda env create -f environment.yml

submodules:  # create conda testing environment
	git submodule init && git submodule update

lint:  # check style with flake8
	source activate amigos-test-env && flake8 --exclude ./honcho/ext,./backup

test: lint  # run unit tests
	source activate amigos-test-env && pytest --ignore ./honcho/ext --cov ./

codecov:  # run codecov
	source activate amigos-test-env && codecov

install: env submodules # install the environment and local source
	source activate amigos-test-env && python setup.py develop

clean:
	find . -name '*.pyc' -delete

deploy: clean # sync the code to the amigos box
	ssh root@amigos "rm -rf /media/mmcblk0p1/*"
	scp -prCB honcho root@amigos:/media/mmcblk0p1

serial: # Connect to triton serial console
	picocom -b 115200 /dev/ttyUSB0

setup-system:
	ssh root@amigos "mount / -o remount,rw"
	# Install laptop ssh key
	cat ~/.ssh/id_rsa_amigos.pub | ssh root@amigos "mkdir -p ~/.ssh && cat > ~/.ssh/authorized_keys"
	# Install bashrc
	scp -pCB system/.bashrc root@amigos:/root
	# Set bash shell for root
	ssh root@amigos "sed -i 's/root:x:0:0:root:\/root:\/bin\/sh/root:x:0:0:root:\/root:\/bin\/bash/g' /etc/passwd"
	# Create windows ssh-key
	ssh root@amigos "ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa_windows -q -N \"\""
	ssh root@amigos "mount / -o remount,ro"

backup: # sync the amigos box sd card
	mkdir -p backup
	scp -prCB root@amigos:/media/mmcblk0p1 "backup/$$(date +%F_%R)"
