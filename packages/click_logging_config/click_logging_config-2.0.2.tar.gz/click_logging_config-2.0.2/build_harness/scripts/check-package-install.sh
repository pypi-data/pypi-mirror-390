#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

set -ex
# diagnostic logging
echo "pwd=$(pwd)"

package_name="${1}"

. ./build_harness/scripts/logging.sh --source-only
setup_logging "check-package-install"

. ./build_harness/scripts/define-uv.sh --source-only
uv_path=$(define_uv)
echo "uv_path=${uv_path}"

# diagnostic logging
ls -l dist/

# WARNING: assumes there is only 1 whl package in dist/
"${uv_path}" pip install "$(ls dist/${package_name}*.whl)"
