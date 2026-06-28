.PHONY: build check indexes pandoc all

build:
	python3 build/scripts/build.py

check:
	python3 build/scripts/check_sources.py

indexes:
	python3 build/scripts/generate_indexes.py

pandoc: build
	python3 build/scripts/build_pandoc.py

all: check build indexes pandoc
