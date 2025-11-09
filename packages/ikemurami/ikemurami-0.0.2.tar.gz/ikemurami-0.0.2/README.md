# pypi-package

Defense against dependency confusion attacks

PyPI: https://pypi.org/project/ikemurami

## Install and run

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "."
python -B examples/main.py
```

## Build & distribute

- Docs: https://packaging.python.org/en/latest/tutorials/packaging-projects/

- Build:

```
python -m pip install --upgrade build
python -m build
```

- Distribute:

```
python -m pip install --upgrade twine
python -m twine upload --repository pypi dist/*
```
