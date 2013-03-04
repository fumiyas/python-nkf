PYTHON=		python

.PHONY: build

default: build

build install:
	$(PYTHON) setup.py $@

clean:
	$(PYTHON) setup.py clean --all

