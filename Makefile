TEST_DIR ?= tests
PROJECT_DIR ?= lima

check:
	@echo "Installing silently and running..."
	@python setup.py install >/dev/null 2>&1;
	pylima

install:
	@echo "Installing requirements..."
	pip install -r requirements.txt

install_test:
	@echo "Installing test requirements..."
	pip install -r requirements-test.txt

precommit_install:
	@echo "Installing pre-commit hooks!"
	@echo "Make sure to first run `make install_test`"
	pre-commit install

lint:
	pylint --rcfile=.pylintrc $(PROJECT_DIR)

black:
	black --line-length 88 $(PROJECT_DIR)

black_check:
	black --line-length 88 --check --diff $(PROJECT_DIR)

unit:
	coverage erase
	coverage run -m pytest --doctest-modules --junitxml=junit/test-results.xml $(TEST_DIR)
	coverage xml -i
