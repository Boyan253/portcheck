.PHONY: test lint clean

test:
	pytest -q

lint:
	python -m compileall -q .

clean:
	rm -rf .pytest_cache __pycache__ .coverage
