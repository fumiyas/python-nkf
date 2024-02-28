PYTHON=		python3
DESTDIR=	/
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
	rm -rf MANIFEST dist __pycache__ *.egg-info

.PHONY: sdist dist
sdist dist:
	SOURCE_DATE_EPOCH=`git log -1 --pretty=%ct` \
	$(PYTHON) -m build --sdist .

.PHONY: bdist wheels
bdist wheels:
	SOURCE_DATE_EPOCH=`git log -1 --pretty=%ct` \
	$(PYTHON) -m build --wheel .

.PHONY: dist-check
dist-check:
	$(PYTHON) -m twine check dist/*

.PHONY: dist-upload
dist-upload:
	$(PYTHON) -m twine upload --repository nkf $(UPLOAD_ARGS)

.PHONY: dist-upload-test
dist-upload-test:
	$(PYTHON) -m twine upload --repository nkf-test $(UPLOAD_ARGS)
