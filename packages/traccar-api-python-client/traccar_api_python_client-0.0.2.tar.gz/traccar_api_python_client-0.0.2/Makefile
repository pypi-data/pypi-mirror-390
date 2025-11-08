VENV_NAME			:= _venv
VENV_BIN			:= ${VENV_NAME}/bin
PYTHON				:= ${VENV_BIN}/python3

TRACCAR_VERSION 	:= 6.10.0
SOURCE_SPEC_URL 	:= https://raw.githubusercontent.com/traccar/traccar/refs/heads/master/openapi.yaml
LOCAL_SPEC_FOLDER	:= ./openapi/traccar/${TRACCAR_VERSION}/
LOCAL_SPEC_FILE 	:= ${LOCAL_SPEC_FOLDER}/openapi.yaml

.DEFAULT: help
.PHONY: help
help:
	@echo "\n Makefile usage\n"
	@echo "\t make build-package \t\t build a distributable python package"
	@echo "\t make clean \t\t\t cleanup"
	@echo "\t make download-spec \t\t download the latest Traccar openapi specification"
	@echo "\t make format \t\t\t format all code"
	@echo "\t make format-check	\t run code formatting check"
	@echo "\t make generate \t\t\t generate the client (from openapi)"
	@echo "\t make lint \t\t\t lint python source files"
	@echo "\t make publish \t\t\t publish the package (PyPI)"
	@echo "\t make test \t\t\t run tests"
	@echo "\t make tox \t\t\t run tests against various python versions"
	@echo "\t make venv \t\t\t setup python virtual environment"

.PHONY: venv
venv:
	$(info creating virtual environment..)
	python3 -m venv $(VENV_NAME)
	$(VENV_BIN)/pip install --upgrade pip build
	$(VENV_BIN)/pip install --group all
	@$(VENV_BIN)/pip freeze
	@$(VENV_BIN)/python --version

.PHONY: build-package
build-package:
	${PYTHON} -m build

.PHONY: clean
clean:
	$(info cleaning up..)
	$(RM) -rf ./${VENV_NAME} && \
	find . -name \*.pyc -delete && \
	$(RM) .coverage
	$(RM) ./coverage.xml
	$(RM) -rf .tox
	$(RM) .python-version
	$(RM) -rf ./dist

.PHONY: download-spec
download-spec:
	mkdir -p ${LOCAL_SPEC_FOLDER}
	curl --output ${LOCAL_SPEC_FILE} ${SOURCE_SPEC_URL}

.PHONY: format
format:
	black src/ tests/

.PHONY: format-check
format-check:
	black --check src/ tests/

.PHONY: generate
generate:
	openapi-python-client generate --path ${LOCAL_SPEC_FILE} \
		--config ./config.yml \
		--output-path ./src \
		--overwrite

.PHONY: lint
lint: format-check
	@${PYTHON} -Im pylint src/ tests/

.PHONY: publish
publish:
	${PYTHON} -Im flit publish

.PHONY: test
test:
	pytest ./tests

.PHONY: tox
tox:
	tox
