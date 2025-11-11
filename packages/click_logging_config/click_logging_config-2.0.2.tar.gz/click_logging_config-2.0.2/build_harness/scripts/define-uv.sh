#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

# WARNING:
#     - Assumes logging from `logging.sh` has been loaded & setup already.


define_uv() {
  local system_uv_path

  system_uv_path=$(command -v uv 2>/dev/null)
  venv_uv_path="${venv_bin}/uv"
  if [[ -f "${venv_uv_path}" ]]; then
    # Venv uv takes priority over system uv
    uv_path=${venv_uv_path}
  else
    # Use uv system path
    if [[ -z "${system_uv_path}" ]]; then
      log_this "ERROR" "uv command not found"
      exit 1
    fi
    uv_path=${system_uv_path}
  fi

  log_this "INFO" "uv_path=${uv_path}"
  echo "${uv_path}"
}
