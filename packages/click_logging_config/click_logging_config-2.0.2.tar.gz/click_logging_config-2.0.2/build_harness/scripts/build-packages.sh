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
setup_logging "build-packages"

. ./build_harness/scripts/define-venv-bin.sh --source-only
venv_bin=$(define_venv)
. ./build_harness/scripts/define-uv.sh --source-only
uv_path=$(define_uv)

DEFAULT_RELEASE="0.0.0"


check_parameter()
{
  local this_value="${1}"
  local error_message="${2}"

  if [ -z "${this_value}" ]; then
    log_this "ERROR" "${error_message}"
    exit 1
  fi
}


current_sha()
{
  git rev-parse --short=8 HEAD
}


undefined_release()
{
  echo "${DEFAULT_RELEASE}+$(current_sha)"
}


apply_release_id() {
  local this_release="${1}"
  check_parameter "${this_release}" "Release ID not provided to apply_release_id"
  local package_dir="${2}"
  check_parameter "${package_dir}" "Package directory not provided to apply_release_id"

  if [ ! -d "${package_dir}" ]; then
    log_this "ERROR" "Package directory '${package_dir}' not found"
    exit 1
  fi
  if [ -f "${package_name}/VERSION" ]; then
    cp "${package_name}/VERSION" "${package_name}/VERSION.bak"
  fi

  echo "${this_release}" > "${package_dir}/VERSION"
}



package_name="${1}"
check_parameter "${package_name}" "Package name not provided"
log_this "INFO" "package_name=${package_name}"
default_branch="${2}"
check_parameter "${default_branch}" "Default branch not provided"
log_this "INFO" "default_branch=${default_branch}"

release_id="${3:-$(undefined_release)}"
log_this "INFO" "release_id=${release_id}"

apply_release_id "${release_id}" "${package_name}"
if ! "${uv_path}" build; then
  log_this "ERROR" "Package build failed"
  exit 1
fi
