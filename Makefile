PYTHON := python
module:=wait_for_it
project:=wait-for-it
version:=$(shell $(PYTHON) -c 'import sys, os; sys.path.insert(0, os.path.abspath(".")); print(__import__("${module}").__version__)')

.PHONY: list
list help:
	@make -pq | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | sed '/Makefile/d' | sort

.PHONY: format
format:
	@$(PYTHON) -m black --version
	@$(PYTHON) -m black $(module) $(ARGS)

.PHONY: format-check
format-check:
	@$(MAKE) format ARGS="--check"

.PHONY: lint
lint:
	@$(PYTHON) -m flake8 --max-line-length 100 $(module)

.PHONY: create-venv
create-venv:
	@test -d venv || $(PYTHON) -m venv venv
	@echo "virtualenv 'venv' created in cwd"

.PHONY: venv
venv: create-venv
	@echo "run the following command to activate the virtual environment: source ./venv/bin/activate"
	@echo "(command copied to clipboard)"
	@echo "source ./venv/bin/activate" | pbcopy

.PHONY: install-deps
install-deps:
	@$(PYTHON) -m pip install -e .

.PHONY: install-deps-dev
install-deps-dev:
	@$(PYTHON) -m pip install -e ".[dev]"

.PHONY: build
build:
	@rm -rf ./dist/*
	@$(PYTHON) setup.py sdist bdist_wheel

.PHONY: test
test:
	@$(PYTHON) -m pytest $(module) $(ARGS)

.PHONY: test-cov
test-cov:
	@$(MAKE) test --cov=api_tools --cov-report=html --cov-report=term --show-capture=all

.PHONY: clean
clean:
	@rm -rf ./dist ./build ./*.egg-info ./htmlcov
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

.PHONY: check
check:
	@$(PYTHON) -m twine check dist/*

.PHONY: tag
tag:
ifeq (,$(shell git tag --list | grep "${version}"))
	@git tag "v${version}"
	@git push --tags
endif

.PHONY: release
release: tag
ifdef version
	@curl -XPOST \
	-H "Authorization: token ${GITHUB_ACCESS_TOKEN}" \
	-H "Content-Type: application/json" \
	"https://api.github.com/repos/hartwork/${project}/releases" \
	--data "{\"tag_name\": \"v${version}\",\"target_commitish\": \"master\",\"name\": \"v${version}\",\"draft\": false,\"prerelease\": false}"
endif

.PHONY: install
install:
	@$(PYTHON) -m pip install --force-reinstall "${project}"

.PHONY: install-test
install-test:
	@$(PYTHON) -m pip install --force-reinstall --index-url https://test.pypi.org/simple "${project}"

.PHONY: upload publish
publish upload: test clean build check release
	@$(PYTHON) -m twine upload dist/*

.PHONY: upload-test
upload-test: test clean build check
	@$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
