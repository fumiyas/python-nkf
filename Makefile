PYTHON=		python3
BUILD=		$(PYTHON) -m build
PDM=		$(PYTHON) -m pdm
TWINE=		$(PYTHON) -m twine

VERSION=	$(shell $(PDM) show --version)

DIST_ENV=	SOURCE_DATE_EPOCH=`git log -1 --pretty=%ct`
DIST_FILES= 	dist/*-$(VERSION).tar.gz

-include Makefile.local

## ======================================================================

.PHONY: default
default: dist

.PHONY: clean
clean:
	$(RM) -r .venv .pdm-* .pytest* __pycache__ build dist pdm.lock src/*/_version.py src/*.egg-info
	find src tests -name __pycache__ -exec $(RM) -r {} +
	find src -name "*.so" -exec $(RM) {} +

.PHONY: test
test:
	$(PDM) install
	$(PDM) run pytest
	
## ======================================================================

.PHONY: dist
dist:
	$(BUILD) .

.PHONY: dist-source
dist-source:
	$(DIST_ENV) \
	$(BUILD) --sdist .

.PHONY: dist-wheel
dist-wheel:
	$(DIST_ENV) \
	$(BUILD) --wheel .

.PHONY: dist-check
dist-check:
	$(TWINE) check --strict dist/*

.PHONY: dist-upload
dist-upload:
	$(RM) dist/*.whl
	$(PDM) publish --no-build --repository pypi-nkf

.PHONY: dist-upload-test
dist-upload-test:
	$(RM) dist/*.whl
	$(PDM) publish --no-build --repository test-pypi-nkf
