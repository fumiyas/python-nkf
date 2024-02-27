PYTHON=		python3
DESTDIR=	/
SDIST_ARGS=	--formats=gztar --owner=root --group=root
UPLOAD_ARGS= 	dist/*.tar.gz

.PHONY: default
default: build

.PHONY: build check
build check:
	$(PYTHON) setup.py $@

.PHONY: install
install:
	$(PYTHON) setup.py install --root $(DESTDIR)

.PHONY: clean
clean:
	$(PYTHON) setup.py clean --all
	rm -rf MANIFEST dist *.pyc

.PHONY: dist
dist:
	SOURCE_DATE_EPOCH=`git log -1 --pretty=%ct` \
	$(PYTHON) setup.py sdist $(SDIST_ARGS)

.PHONY: dist-check
dist-check:
	twine check dist/*

.PHONY: dist-upload
dist-upload:
	twine upload --repository nkf $(UPLOAD_ARGS)
