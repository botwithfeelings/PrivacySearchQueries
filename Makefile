# Most of the contents of this make file is courtesy of Professor
# Tim Menzies, Dept. of CSC, NC State Univerisity. See
# https://github.com/txt/se16/blob/master/Makefile for the original.
asave: add save

acommit: add commit

add: ready
	@- git add -A

save: ready
	@- git status
	@- git commit -am "saving"
	@- git push origin master

commit: ready
	@- git status
	@- git commit -a
	@- git push origin master

update: ready
	@- git pull origin master

status: ready
	@- git status

ready:
	@git config --global credential.helper cache
	@git config credential.helper 'cache --timeout=3600'
