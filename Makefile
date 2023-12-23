recursive-wildcard=$(foreach d,$(wildcard $(1:=/*)),$(call recursive-wildcard,$d,$2) $(filter $(subst *,%,$2),$d))

PYTHON := python3.12
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
PYPROJECT_FILES := $(call recursive-wildcard,., *pyproject.toml)

$(VENV_DIR)/create_dev_venv_stamp:
	$(PYTHON) -m venv --clear $(VENV_DIR)
	$(VENV_PYTHON) -m pip install --upgrade "pip>=21.3"
	touch $@

.PHONY: create-dev-venv
create-dev-venv: $(VENV_DIR)/create_dev_venv_stamp

$(VENV_DIR)/init_dev_venv_stamp: $(PYPROJECT_FILES) | create-dev-venv
	$(VENV_PYTHON) -m pip install --editable booking-server[dev] --editable booking-client[dev] --config-settings editable_mode=compat
	$(VENV_PYTHON) -m pip install --editable booking-common[dev] --config-settings editable_mode=compat
	touch $@

.PHONY: init-dev-venv
init-dev-venv: $(VENV_DIR)/init_dev_venv_stamp

.PHONY: check-format
check-format: init-dev-venv
	$(VENV_PYTHON) -m black  --check --config black.toml .

.PHONY: format
format: init-dev-venv
	$(VENV_PYTHON) -m black  --config black.toml .

.PHONY: check-imports
check-imports: init-dev-venv
	$(VENV_PYTHON) -m isort --check-only --settings isort.toml .

.PHONY: sort-imports
sort-imports: init-dev-venv
	$(VENV_PYTHON) -m isort --settings isort.toml .

.PHONY: check-lint
check-lint: init-dev-venv
	$(VENV_PYTHON) -m pylint --rcfile pylintrc.toml --recursive=y .

.PHONY: check-types
check-types: init-dev-venv
	$(VENV_PYTHON) -m mypy --config-file mypy.toml .

.PHONY: check
check: check-format check-imports check-lint check-types

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
