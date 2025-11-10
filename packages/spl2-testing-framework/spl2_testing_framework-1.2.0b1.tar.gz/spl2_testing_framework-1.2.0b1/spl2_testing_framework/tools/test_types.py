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

import logging
from collections import UserDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator

_LOGGER = logging.getLogger(__name__)


@dataclass
class Test:
    name: str
    meta: dict = field(default_factory=dict, init=False)

    @property
    def test_id(self) -> str:
        return self.name


@dataclass
class SingleSPL2(Test):
    input: str
    code_module_path: Path


@dataclass
class BoxTest(Test):
    input: str
    output: list
    module_path: Path
    code_module_path: Path
    metrics: list = field(default_factory=list)


@dataclass
class UnitTest(Test):
    file_path: Path
    file_name: str
    content: str
    code_module_path: Path

    @property
    def test_id(self) -> str:
        return self.file_name + "__" + self.name


@dataclass
class TestSuite(UserDict):
    tests: Dict[str, Test] = field(default_factory=dict)

    def add(self, test: Test) -> None:
        if test.test_id not in self.tests:
            self.tests[test.test_id] = test
        else:
            _LOGGER.warning(
                f"Test {test.test_id} already exists, name will be modified"
            )
            test_name = self.__calculate_new_name(test.test_id)
            self.tests[test_name] = test

    def __calculate_new_name(self, name: str) -> str:
        return name + "__" + str(len(self.tests))

    def __iter__(self):
        return iter(self.tests.values())

    def get_ids(self) -> Iterator[str]:
        return iter(self.tests)
