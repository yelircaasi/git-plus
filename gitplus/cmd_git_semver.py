#!/usr/bin/env python3
# Copyright 2013 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import argparse

from . import git
from . import semver

from typing import *


def main():
    git.assert_in_git_repository()

    parser = argparse.ArgumentParser(description='List / update semver tags')

    parser.add_argument('--major', action='store_true', default=False, help='Increase major version')
    parser.add_argument('--minor', action='store_true', default=False, help='Increase minor version')
    parser.add_argument('--patch', action='store_true', default=False, help='Increase patch version')
    parser.add_argument('--suffix', type=str, default="", help='Suffix (for example v1.2.3-suffix)')

    args = parser.parse_args()
    incr_major: bool = args.major
    incr_minor: bool = args.minor
    incr_patch: bool = args.patch
    suffix: str = args.suffix

    versions = semver.get_all_versions_ordered(output_non_versions=True)
    max_version = versions[-1] if versions else semver.Version("v0.0.0", "v", 0, 0, 0, "")

    if not versions:
        print("No tags")
        sys.exit(0)

    if incr_major or incr_minor or incr_patch:
        if incr_patch:
            max_version.patch += 1
        if incr_minor:
            max_version.minor += 1
            max_version.patch = 0
        if incr_major:
            max_version.major += 1
            max_version.minor = 0
            max_version.patch = 0
        new_tag = f'{max_version.prefix}{max_version.major}.{max_version.minor}.{max_version.patch}'
        if suffix:
            new_tag += "-" + suffix
        print(f"Creating new version/tag: {new_tag}")
        success, output = git.execute_git(f"tag {new_tag}")
        if not success:
            print(f'Error creating tag: {output}')
            sys.exit(1)
        print(f'Tag {new_tag} created, you can push it now')
    else:
        for n, version in enumerate(versions):
            if n > 0:
                previous_ver = versions[n-1]
                if previous_ver.major != version.major:
                    print(f"New major: {version.major}")
                if previous_ver.minor != version.minor:
                    print(f"New minor: {version.major}.{version.minor}")
            print(f" * {version.tag}")
        print()
        print(f"Last version: {max_version.tag}")
        print()