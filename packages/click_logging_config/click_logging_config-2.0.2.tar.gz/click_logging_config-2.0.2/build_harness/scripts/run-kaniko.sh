#!/usr/bin/env bash
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

# NOTE: This script is intended to be used inside a Kaniko container :
#       `gcr.io/kaniko-project/executor`

set -ex

BUILD_IMAGE_VENV_PATH="/venv"
KANIKO_DOCKER_DIR="/kaniko/.docker"

python_version=$(echo "${1}" | xargs)
image_path=$(echo "${2}" | xargs)
project_name=$(echo "${3}" | xargs)
project_dir=$(echo "${4:-/tmp}" | xargs)
registry=$(echo "${5}" | xargs)
registry_user=$(echo "${6}" | xargs)
registry_password=$(echo "${7}" | xargs)

kaniko_config="${KANIKO_DOCKER_DIR}/config.json"

if [[ -z "${registry}" ]]; then
  echo "Empty container registry parameter, so not generating ${kaniko_config}" \
    >/dev/stdout
  [ $(/kaniko/executor \
    --build-arg venv_path="${BUILD_IMAGE_VENV_PATH}" \
    --build-arg project_dir="${project_dir}" \
    --build-arg project_name="${project_name}" \
    --build-arg python_version="${python_version}" \
    --context "${project_dir}" \
    --destination "${image_path}" \
    --dockerfile "${project_dir}/docker/ci/Dockerfile" \
    --no-push) ] || (echo "Kaniko failed to build" >/dev/stdout; exit 1)
else
  mkdir -p "${KANIKO_DOCKER_DIR}"
  echo "{\"auths\":{\"${registry}\":{\"username\":\"${registry_user}\",\"password\":\"${registry_password}\"}}}" \
    > "${kaniko_config}"
  /kaniko/executor \
    --build-arg venv_path="${BUILD_IMAGE_VENV_PATH}" \
    --build-arg project_dir="${project_dir}" \
    --build-arg project_name="${project_name}" \
    --build-arg python_version="${python_version}" \
    --context "${project_dir}" \
    --destination "${image_path}" \
    --dockerfile "${project_dir}/docker/ci/Dockerfile"
fi
