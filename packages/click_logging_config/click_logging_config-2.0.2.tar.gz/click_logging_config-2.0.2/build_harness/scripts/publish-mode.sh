#!/usr/bin/env bash
#
# Copyright (c) 2025 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

# WARNING:
#     - Assumes set_publish_mode from `publish-mode.sh` has been loaded already.

set_publish_mode()
{
  local local_ci_commit_tag="${1}"
  local local_ci_pipeline_source="${2}"

  if [ "${local_ci_pipeline_source}" == "merge_request_event" ] || [[ -z "${local_ci_commit_tag}" ]]; then
    # Any untagged commit on local_ci_default_branch branch is a dry run.
    # Any merge request pipeline is a dry run.
    # Any feature branch commit is a dry run.
    PUBLISH_THIS="dryrun";
  elif [ ! -z "${local_ci_commit_tag}" ]; then
    # Non-empty commit tags cause a publish
    PUBLISH_THIS="yes";
  else
    PUBLISH_THIS="dryrun";
  fi

  # log PUBLISH_THIS to pipeline log for debugging
  echo "${PUBLISH_THIS}"
}
