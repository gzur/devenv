.PHONY: uninstall install

install:
	@python setup.py install --record .installed_files \

develop:
	@python setup.py develop --record .installed_files \

uninstall:
	@cat .installed_files | xargs rm -v
	@rm .installed_files

test:
	nosetests tests/unittests/

test_debug:
	nosetests -s --nocapture tests/unittests/

black:
	black -Sl100 devenv/ tests/