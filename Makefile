PYTHON=		python

.PHONY: build dist

default: build

build install:
	$(PYTHON) setup.py $@

clean:
	$(PYTHON) setup.py clean --all
	rm -rf dist

dist:
	$(PYTHON) setup.py sdist

