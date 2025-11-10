#
#   Copyright 2025 Splunk Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import argparse
import logging
import sys

import pytest

from spl2_testing_framework.tools.test_types import SingleSPL2

_LOGGER = logging.getLogger(__name__)


def test_single_spl2_file(spl2_test_runner, single_spl2_file: SingleSPL2):
    _LOGGER.info(f"Executing single SPL2 File: '{single_spl2_file.name}'")
    _LOGGER.debug(f"Single SPL2 File Details: {single_spl2_file}")
    spl2_test_runner.run_single_spl2_file(single_spl2_file)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("type")

    arguments, other = parser.parse_known_args()

    args = [__file__, "--type", arguments.type]
    args.extend(other)

    # INFO log level is required for result printing
    if "--log-cli-level" not in args:
        args.append("--log-cli-level")
        args.append("INFO")

    sys.exit(pytest.main(args))


if __name__ == "__main__":
    run()
