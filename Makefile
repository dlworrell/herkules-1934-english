.PHONY: build check

build:
	python3 build/scripts/build.py

check:
	python3 build/scripts/check_sources.py
