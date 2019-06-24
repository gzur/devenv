.PHONY: uninstall install install_test_requirements test_docker_in_docker

install:
	@python setup.py install --record .installed_files \

develop:
	@python setup.py develop --record .installed_files \

uninstall:
	@cat .installed_files | xargs rm -v
	@rm .installed_files

install_test_requirements:
	pip install -qr requirements.txt
	pip install -qr test-requirements.txt

test: install_test_requirements
	pytest tests/unittests/

black:
	black -Sl100 devenv/ tests/

test_docker_in_docker: test_alpine test_debian


test_alpine:
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`:/app/ -w /app/ python:alpine3.7 /app/tests/dind/dind-alpine-test.sh
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`:/app/ -w /app/ python:alpine3.6 /app/tests/dind/dind-alpine-test.sh

test_debian:
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`:/app/ -w /app/ python:2.7 /app/tests/dind/dind-debian-test.sh
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`:/app/ -w /app/ python:3.7 /app/tests/dind/dind-debian-test.sh