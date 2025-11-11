#!/usr/bin/env bash
#
# Copyright (c) 2025 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

. ./build_harness/scripts/logging.sh --source-only
setup_logging "publish-packages"

. ./build_harness/scripts/publish-mode.sh --source-only

any_errors=""

result1=$(set_publish_mode \
  "" \
  "merge_request_event")
if [ "dryrun" != "${result1}" ]; then
  echo "FAILED: merge request event not dry run (${result1})"
  any_errors=1
fi

result2=$(set_publish_mode \
  "" \
  "push_event")
if [ "dryrun" != "${result2}" ]; then
  echo "FAILED: feature branch push event not dry run (${result2})"
  any_errors=1
fi

result3=$(set_publish_mode \
  "3.1.4" \
  "tag_event")
if [ "yes" != "${result3}" ]; then
  echo "FAILED: tag event not publishing (${result3})"
  any_errors=1
fi

result4=$(set_publish_mode \
  "3.1.4" \
  "push_event")
if [ "yes" != "${result4}" ]; then
  echo "FAILED: push event not publishing (${result4})"
  any_errors=1
fi

[[ -z "${any_errors}" ]] && (echo "SUCCESS: test-publish-packages.sh") || (exit 1)
