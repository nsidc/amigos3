# ~/.bashrc: executed by bash(1) for non-login shells.

export PS1='\h:\w\$ '

umask 077

set -o vi

alias ls='ls -la --color=auto'
alias honcho='python /media/mmcblk0p1/honcho/cli.py'
