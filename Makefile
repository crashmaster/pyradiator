THIS_FILE := $(abspath $(lastword $(MAKEFILE_LIST)))
PACKAGE_NAME := pyradiator
PYTHON3 := env python3

REPO_DIR := $(patsubst %/,%,$(dir $(THIS_FILE)))

PACKAGE_DIR := $(REPO_DIR)/build

RUN_BUILD := $(PYTHON3) setup.py --quiet sdist --dist-dir $(PACKAGE_DIR)
RUN_CLEAR := rm -rf $(PACKAGE_DIR)
RUN_PYRADIATOR := tox -c $(REPO_DIR)/tox_run.ini
RUN_TESTS := tox -c $(REPO_DIR)/tox_test.ini
SHOW_PACKAGE := find $(PACKAGE_DIR) -name '*.tar.gz'


all: test


build: clear
	@$(RUN_BUILD)
	@$(SHOW_PACKAGE)

clear:
	@$(RUN_CLEAR)

run:
	@$(RUN_PYRADIATOR)

test:
	@$(RUN_TESTS)


.PHONY: \
	all \
	build \
	clear \
	run \
	test
