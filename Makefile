.PHONY: install test lint demo api dashboard

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

demo:
	python scripts/run_demo.py

api:
	uvicorn llm_guardian.api:app --reload

dashboard:
	streamlit run dashboard/app.py

