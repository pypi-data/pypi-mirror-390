#!/bin/sh
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.

set -ex

project_root="${1}"

mkdir -p reports
hadolint \
  -f gitlab_codeclimate \
  "${project_root}/docker/ci/Dockerfile" \
  > "reports/hadolint-$(md5sum "${project_root}/docker/ci/Dockerfile" | cut -d" " -f1).json"
