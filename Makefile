PYTHON=		python3
DESTDIR=	/
SDIST_ARGS=	--formats=bztar --owner=root --group=root

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
	$(PYTHON) setup.py sdist $(SDIST_ARGS)

upload:
	$(PYTHON) setup.py sdist $(SDIST_ARGS) upload --sign

