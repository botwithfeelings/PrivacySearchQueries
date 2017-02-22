# Most of the contents of this make file is courtesy of Professor
# Tim Menzies, Dept. of CSC, NC State Univerisity. See
# https://github.com/txt/se16/blob/master/Makefile for the original.
save: st add sv ud ul

commit: st add c ud ul

add: rdy
	@- git add -A

sv: st add
	@- git commit -am "saving"

c: st add
	@- git commit -a

ul: rdy ud
	@- git push origin master

ud: rdy
	@- git pull origin master

st: rdy
	@- git status

rdy:
	@git config --global credential.helper cache
	@git config credential.helper 'cache --timeout=3600'
