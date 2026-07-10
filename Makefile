# ATAP-M8 — one-command reproducibility.
# Data (~GBs) is gitignored; `make data` fetches it. Analyses read the single config.yaml.
PY ?= python3

.PHONY: help setup test lint data harmonize analysis figures all clean

help:
	@echo "make setup     - install Python dependencies"
	@echo "make test      - run the unit test suite (no big data needed)"
	@echo "make data      - download all public datasets -> data/raw (+ MANIFEST)"
	@echo "make harmonize - build analysis-ready tables -> data/processed"
	@echo "make analysis  - run all analysis modules (M1-M10 + extensions)"
	@echo "make figures   - regenerate every figure -> outputs/figures"
	@echo "make all       - data -> harmonize -> analysis -> figures"

setup:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest tests/ -q

lint:
	$(PY) -m pyflakes src/ figures/ tests/ || true

data:
	$(PY) src/data/fetch_data.py

harmonize:
	$(PY) src/data/harmonize.py

analysis:
	$(PY) src/backbone.py
	$(PY) src/confounders.py
	$(PY) src/multiverse.py
	$(PY) src/stratify.py
	$(PY) src/panmimetic.py
	$(PY) src/ablation.py
	$(PY) src/tipping_point.py
	$(PY) src/spatial_run.py
	$(PY) src/survival.py
	$(PY) src/singlecell.py
	$(PY) src/validation.py
	$(PY) src/priorart.py

figures:
	@for f in figures/fig_*.py; do echo ">> $$f"; $(PY) $$f; done

all: harmonize analysis figures
	@echo "Pipeline complete. Figures in outputs/figures/, reports in outputs/logs/."

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
