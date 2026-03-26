UV=			uv
UVX=			uvx
TOX=			$(UV) run tox
SOURCE_DATE_EPOCH=	$(shell git log -1 --pretty=%ct)

DIST_ENV=		SOURCE_DATE_EPOCH="$(SOURCE_DATE_EPOCH)"

-include Makefile.local

## ======================================================================

.PHONY: default
default: dist

.PHONY: clean
clean:
	$(RM) -r .tox .venv dist uv.lock src/*.egg-info
	find src tests -name __pycache__ -exec $(RM) -r {} +
	find src -name "*.so" -exec $(RM) {} +

.PHONY: test
test:
	$(UV) sync --group dev
	$(TOX)
	
## ======================================================================

.PHONY: dist
dist:
	$(DIST_ENV) \
	$(UV) build

.PHONY: dist-source
dist-source:
	$(DIST_ENV) \
	$(UV) build --sdist

.PHONY: dist-wheel
dist-wheel:
	$(DIST_ENV) \
	$(UV) build --wheel

.PHONY: dist-check
dist-check:
	$(UVX) twine check --strict dist/*

.PHONY: dist-upload
dist-upload:
	$(RM) dist/*.whl
	$(UV) publish --index pypi-nkf dist/*

.PHONY: dist-upload-test
dist-upload-test:
	$(RM) dist/*.whl
	$(UV) publish --index test-pypi-nkf dist/*
