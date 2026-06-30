.PHONY: build check indexes glossary pandoc all edt-check edt-pilot edt-report edt-html

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

edt-check:
	python3 -m edt init-project --help >/dev/null
	@echo "EDT dependency is available."

edt-pilot:
	@echo "EDT pilot placeholder: run a small HERKULES page-range pipeline using edt/project.yml."

edt-report:
	@echo "EDT report placeholder: generate OCR, semantic, translation, and accessibility reports."

edt-html:
	@echo "EDT HTML placeholder: generate semantic HTML output after EDT command wiring is finalized."

all: check build indexes glossary pandoc
