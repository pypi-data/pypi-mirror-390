#!/bin/bash
#
# Copyright (c) 2023 Russell Smiley
#
# This file is part of build_harness.
#
# You should have received a copy of the MIT License along with build_harness.
# If not, see <https://opensource.org/licenses/MIT>.

# File containing the list of packages
input_file="${1}"

# File to write the output to
output_file="${2}"

# Empty the output file if it already exists
echo "" > "${output_file}"

# Read the input file line by line
while IFS= read -r package_name; do
    # Get the version of the package
    version=$(apt list -a "${package_name}" 2>/dev/null | grep -E "^${package_name}/" | awk -F'[/ ]' '{print $3}' | head -n 1)

    # If a version is found, append it to the package name and write to the output file
    if [ ! -z "$version" ]; then
        echo "${package_name}=${version}" >> "${output_file}"
    fi
done < "${input_file}"
