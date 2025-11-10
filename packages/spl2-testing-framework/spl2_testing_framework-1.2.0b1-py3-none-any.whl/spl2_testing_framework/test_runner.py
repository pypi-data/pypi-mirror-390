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
import sys
from logging import getLogger

import pytest

from spl2_testing_framework.tools.test_types import BoxTest

_LOGGER = getLogger(__name__)


def test_box_tests(spl2_test_runner, box_test: BoxTest):
    _LOGGER.info("Running box test: %s from \n %s", box_test.name, box_test.module_path)
    _LOGGER.debug("Test details: %s", box_test)

    spl2_test_runner.run_box_test(box_test)


def test_spl2_unit_tests(spl2_test_runner, unit_test):
    _LOGGER.info("Running unit test: %s", unit_test.name)
    _LOGGER.debug("Test details: %s", unit_test)

    spl2_test_runner.run_unit_test(unit_test)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("type")

    arguments, other = parser.parse_known_args()

    args = [__file__, "--type", arguments.type]

    if "--log-cli-level" not in args:
        args.append("--log-cli-level")
        args.append("INFO")

    args.extend(other)
    sys.exit(pytest.main(args))


if __name__ == "__main__":
    run()
