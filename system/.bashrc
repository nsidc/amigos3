# ~/.bashrc: executed by bash(1) for non-login shells.

export PS1='\h:\w\$ '

umask 077

set -o vi


alias ls='ls --color=auto'
alias amigos='python /media/mmcblk0p1/amigos/cli.py'

export PYTHONPATH="${PYTHONPATH}:/media/mmcblk0p1/"
export LD_LIBRARY_PATH=/media/mmcblk0p1/amigos/thumb/
