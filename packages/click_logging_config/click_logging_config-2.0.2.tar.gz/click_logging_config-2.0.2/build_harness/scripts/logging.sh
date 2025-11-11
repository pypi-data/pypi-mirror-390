#!/bin/bash
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.


setup_logging() {
  local log_name="$1"

  # Create logs directory if it doesn't exist
  mkdir -p logs

  # Define log file with timestamp
  log_path="logs/${log_name}-$(date -Iseconds).log"

  # Ensure log file is created and writable
  touch "${log_path}"

  # Log to both file and stderr
  exec 2> >(tee -a "${log_path}" >&2)
}


# Logging function with different levels
log_this() {
  local level="$1"
  shift
  local message="$*"
  local timestamp=$(date -Iseconds)

  case "${level}" in
    "INFO"|"WARN"|"ERROR"|"DEBUG")
      echo "[${timestamp}] [${level}]  ${message}" >/dev/stderr
      ;;
    *)
      echo "[${timestamp}] [ERROR]  Invalid log level, ${level}, ${message}" >/dev/stderr
      ;;
  esac
}
