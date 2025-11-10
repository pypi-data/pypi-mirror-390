# clang-tidy-junit
* Install by running `pip install clang-tidy-junit`.
* Use as `clang-tidy-junit input.log output.xml`

## Development
* Setup dev environment `python3 -m pip install -Ue .[dev]`
* Format the code `black *.py`
* Setup a pre-commit hook `black --check *.py && coverage run -m unittest && coverage report && mypy && pylint *.py`
* Create distribution `python3 -m build ; twine upload dist/*`
