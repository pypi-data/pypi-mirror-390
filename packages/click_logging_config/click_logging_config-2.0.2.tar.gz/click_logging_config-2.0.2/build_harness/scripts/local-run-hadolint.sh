#!/usr/bin/env bash
#
# Copyright (c) 2025 Russell Smiley
#
# This file is part of click_logging_config.
#
# You should have received a copy of the MIT License along with click_logging_config.
# If not, see <https://opensource.org/licenses/MIT>.
#

nerdctl run \
  --rm \
  -it \
  -v $(realpath .):/media \
  -w /media \
  hadolint/hadolint:v2.5.0-debian \
  ./build_harness/scripts/run-hadolint.sh "."
