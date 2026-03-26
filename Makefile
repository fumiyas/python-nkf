UV=			uv
UVX=			uvx
TOX=			UV_PYTHON_PREFERENCE=managed $(UV) run tox
TEST_PYTHONS=		3.10 3.11 3.12 3.13 3.14
SOURCE_DATE_EPOCH=	$(shell git log -1 --pretty=%ct)

DIST_ENV=		SOURCE_DATE_EPOCH="$(SOURCE_DATE_EPOCH)"

-include Makefile.local

## ======================================================================

.PHONY: default
default: dist

.PHONY: clean
clean:
	$(RM) -r .tox .venv .pdm-* .pytest* __pycache__ build dist pdm.lock uv.lock src/*/_version.py src/*.egg-info
	find src tests -name __pycache__ -exec $(RM) -r {} +
	find src -name "*.so" -exec $(RM) {} +

.PHONY: test
test:
	$(UV) sync --group dev
	$(UV) python install $(TEST_PYTHONS)
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
