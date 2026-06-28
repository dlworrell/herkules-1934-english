.PHONY: build check indexes

build:
	python3 build/scripts/build.py

check:
	python3 build/scripts/check_sources.py

indexes:
	python3 build/scripts/generate_indexes.py
