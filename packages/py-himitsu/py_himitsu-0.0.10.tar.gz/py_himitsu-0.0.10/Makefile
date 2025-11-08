VERSION=$(shell python scripts/version.py)
DESTDIR=/
PREFIX=/usr

whl := dist/py_himitsu-$(VERSION)-py3-none-any.whl

all: check lint build

check:
	PYTHONPATH=src python -m unittest tests/test*

lint:
	ruff check -q .

build:
	python3 -m build

$(whl):
	python3 -m build -w

install: $(whl)
	python -m installer --destdir=$(DESTDIR) --prefix=$(PREFIX) $(whl)

clean:
	rm -rf dist
	rm -rf __pycache__
	rm -rf src/himitsu/__pycache__
