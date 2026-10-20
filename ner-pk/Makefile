# Makefile for Pakistani NER System (TechFest NER Challenge)

PYTHON = python

.PHONY: help install scrape clean synth preannotate train evaluate demo test

help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies from requirements.txt"
	@echo "  make scrape        Run polite public scraper"
	@echo "  make clean_data    Clean and normalize scraped raw documents"
	@echo "  make synth         Generate synthetic PHONE_NUMBER, ID_NUMBER, and rare templates"
	@echo "  make preannotate   Run rules + gazetteers pre-annotation"
	@echo "  make split         Create zero-overlap train/dev/benchmark splits"
	@echo "  make train         Fine-tune NER model"
	@echo "  make evaluate      Run seqeval and error analysis"
	@echo "  make demo          Launch Gradio web app"
	@echo "  make test          Run regex and unit tests"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -p "*test*.py"

scrape:
	$(PYTHON) src/scrape.py

clean_data:
	$(PYTHON) src/clean.py

synth:
	$(PYTHON) src/synth.py

preannotate:
	$(PYTHON) src/preannotate.py

split:
	$(PYTHON) src/dataset.py --split

train:
	$(PYTHON) src/train.py

evaluate:
	$(PYTHON) src/evaluate.py

demo:
	$(PYTHON) app/app.py
