#!/usr/bin/env bash
#
# Copyright (c) 2025 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

python_version="${1}"

BUILD_IMAGE_PATH="{CI_REGISTRY_IMAGE}/build-image:${python_version}-${CI_COMMIT_SHORT_SHA}"
PROJECT_NAME=click-logging-config

nerdctl run \
  --entrypoint "" \
  --rm \
  -it \
  -v $(realpath .):/media \
  -w /media \
  gcr.io/kaniko-project/executor:debug \
  /bin/sh -c "source ./build_harness/scripts/run-kaniko.sh \
    "${python_version}" \
    "${BUILD_IMAGE_PATH}" \
    "${PROJECT_NAME}" \
    ".""
