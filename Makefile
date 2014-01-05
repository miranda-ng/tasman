.PHONY: help install test

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  install    to install tasman with all dependencies"
	@echo "  test       to run test suite"

install:
	pip install -e ./ -r requirements.txt

test:
	@python2 ./tasman/tests/__init__.py

run:
	@xmppflask ./tasman/app.py:app
