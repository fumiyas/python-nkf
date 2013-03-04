PYTHON=		python
DESTDIR=	/

.PHONY: build dist

default: build

build:
	$(PYTHON) setup.py $@

install:
	$(PYTHON) setup.py install --root $(DESTDIR)

clean:
	$(PYTHON) setup.py clean --all
	rm -rf MANIFEST dist *.pyc

dist:
	$(PYTHON) setup.py sdist --formats=bztar --owner=root --group=root

