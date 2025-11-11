#!/usr/bin/env bash
#
# Copyright (c) 2025 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

set -ex

ci_commit_tag=${1:-""}
ci_pipeline_source=${2:-""}

. ./build_harness/scripts/logging.sh --source-only
setup_logging "publish-packages"

. ./build_harness/scripts/publish-mode.sh --source-only

log_this "DEBUG" "ci_commit_tag: ${ci_commit_tag}"
log_this "DEBUG" "ci_pipeline_source: ${ci_pipeline_source}"

set_publish_mode \
  "${ci_commit_tag}" \
  "${ci_pipeline_source}"
