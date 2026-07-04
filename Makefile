.PHONY: build check indexes glossary pandoc all edt-check edt-pilot edt-pilot-check edt-report edt-html

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
	python3 -c "import edt.cli"
	@echo "EDT dependency is available."

edt-pilot:
	python3 build/scripts/edt_pilot.py
	python3 build/scripts/check_edt_pilot_outputs.py

edt-pilot-check:
	python3 build/scripts/check_edt_pilot_outputs.py

edt-report: edt-pilot
	@echo "EDT pilot status: reports/pilot/pilot-status.json"

edt-html: edt-pilot
	@echo "EDT pilot HTML: output/pilot/html/herkules-pilot.html"

all: check build indexes glossary pandoc
