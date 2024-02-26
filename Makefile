PYTHON=		python3
DESTDIR=	/
SDIST_ARGS=	--formats=gztar --owner=root --group=root
SIGN_ID=	fumiyas@osstech.co.jp

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
	twine upload --repository nkf --sign --identity $(SIGN_ID) dist/*.tar.gz
