#!/bin/bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

# WARNING: Assumes logging from `logging.sh` has been loaded & setup already.

define_venv() {
  local venv_bin

  [[ -d "/venv" ]] && {
    # venv directory is in the root directory in a pipeline container
    venv_bin="/venv/bin"
  } || {
    [[ -d ".venv" ]] && {
      # venv directory is in the local directory when run locally
      venv_bin=".venv/bin"
    } || {
      log_this "ERROR" "Could not find venv directory"
      exit 1
    }
  }

  log_this "INFO" "Using venv directory, ${venv_bin}"
  echo "${venv_bin}"
}
