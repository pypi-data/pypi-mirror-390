#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

set -ex

expected_python_version="${1:-3.12}"

. ./build_harness/scripts/logging.sh --source-only
setup_logging "set-python-release"

. ./build_harness/scripts/define-venv-bin.sh --source-only
venv_bin=$(define_venv)
. ./build_harness/scripts/define-uv.sh --source-only
uv_path=$(define_uv)

log_this "DEBUG" "pwd=$(pwd)"

output=$("${uv_path}" run python --version)

if [[ "${output}" == *"${expected_python_version}"* ]]; then
  # output contains the expected version
  "${uv_path}" venv
else
  # create a uv venv for the specified version
  "${uv_path}" venv "$(dirname "${venv_bin}")"
  "${uv_path}" python install "${expected_python_version}"
  "${uv_path}" python pin "${expected_python_version}"

fi
