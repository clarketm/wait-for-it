.PHONY: list
list help:
	@make -pq | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | sed '/Makefile/d' | sort

.PHONY: format
format:
	python -m black .

.PHONY: build
build:
	rm -rf ./dist/*
	python3 setup.py sdist bdist_wheel

.PHONY: test
test:
	@echo "not implemented"

.PHONY: clean
clean:
	rm -rf ./dist ./build ./*.egg-info ./htmlcov
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: check
check:
	twine check dist/*

.PHONY: upload-test
upload-test: test clean build check
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: upload
upload: test clean build check
	twine upload dist/*

