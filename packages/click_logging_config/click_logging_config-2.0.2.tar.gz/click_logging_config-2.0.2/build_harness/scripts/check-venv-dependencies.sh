#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

set -e

. ./build_harness/scripts/logging.sh --source-only
setup_logging "check-venv-dependencies"

. ./build_harness/scripts/define-venv-bin.sh --source-only
venv_bin=$(define_venv)
. ./build_harness/scripts/define-uv.sh --source-only
uv_path=$(define_uv)


if ! "${uv_path}" sync --all-extras; then
  log_this "ERROR" "Checking virtual env dependencies failed"
  exit 1
fi
