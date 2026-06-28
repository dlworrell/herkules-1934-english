.PHONY: build check indexes glossary pandoc all

build:
	python3 build/scripts/build.py

check:
	python3 build/scripts/check_sources.py

indexes:
	python3 build/scripts/generate_indexes.py

glossary:
	python3 build/scripts/generate_glossary.py

pandoc: build
	python3 build/scripts/build_pandoc.py

all: check build indexes glossary pandoc
