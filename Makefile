.PHONY: build upload

# python -m build --wheel .
# python -m build --sdist .

build:
	rm -rf dist/ build/
	python -m pip install build
	python -m build .

upload:
	python -m pip install twine
	python -m twine upload dist/openai-*
	rm -rf dist
