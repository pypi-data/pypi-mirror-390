#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

set -ex

. ./build_harness/scripts/logging.sh --source-only
setup_logging "check-linting"

. ./build_harness/scripts/define-venv-bin.sh --source-only
venv_bin=$(define_venv)
echo "venv_bin=${venv_bin}"

# diagnostic logging
ls "${venv_bin}"

# NOTE: `ruff` is technically not a linting tool, but `mypy` is.
"${venv_bin}/ruff" check
"${venv_bin}/mypy" click_logging_config
