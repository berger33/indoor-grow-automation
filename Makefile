.PHONY: quality test secrets

quality:
	python scripts/quality_gate.py

test:
	python -m unittest discover -s tests -v

secrets:
	python scripts/secret_scan.py --tracked
