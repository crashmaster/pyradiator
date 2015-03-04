PACKAGE := pyradiator

PYTHON2 := env python2
PYTHON3 := env python3

THIS_FILE := $(abspath $(lastword $(MAKEFILE_LIST)))
REPO_DIR := $(patsubst %/,%,$(dir $(THIS_FILE)))
TEST_DIR := $(REPO_DIR)/$(PACKAGE)/test
PACKAGE_DIR := $(REPO_DIR)/build

RUN_TESTS_PY2 := PYTHONPATH=$(REPO_DIR)/$(PACKAGE) $(PYTHON2) $(TEST_DIR)/test_$(PACKAGE).py
RUN_TESTS_PY3 := PYTHONPATH=$(REPO_DIR)/$(PACKAGE) $(PYTHON3) $(TEST_DIR)/test_$(PACKAGE).py

.PHONY: all test2 test3 test clear build

all: test

test2:
	@printf '------------------------\n'
	@printf 'Smoke tests with Python2\n'
	@printf '------------------------\n\n'
	@$(RUN_TESTS_PY3)

test3:
	@printf '------------------------\n'
	@printf 'Smoke tests with Python3\n'
	@printf '------------------------\n\n'
	@$(RUN_TESTS_PY3)

test: test2 test3

clear:
	@rm -rf $(PACKAGE_DIR)

build: clear
	@$(PYTHON2) setup.py --quiet sdist --dist-dir $(PACKAGE_DIR)
	@find $(PACKAGE_DIR) -name '*.tar.gz'
