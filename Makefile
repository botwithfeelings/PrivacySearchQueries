# Most of the contents of this make file is courtesy of Professor
# Tim Menzies, Dept. of CSC, NC State Univerisity. See
# https://github.com/txt/se16/blob/master/Makefile for the original.
save: status add saving update upload

commit: status add committing update upload

saving:
	@-git commit -am "saving"

committing:
	@- git commit -a

upload: ready
	@- git push origin master

update: ready
	@- git pull origin master

status: ready
	@- git status

ready:
	@git config --global credential.helper cache
	@git config credential.helper 'cache --timeout=3600'
