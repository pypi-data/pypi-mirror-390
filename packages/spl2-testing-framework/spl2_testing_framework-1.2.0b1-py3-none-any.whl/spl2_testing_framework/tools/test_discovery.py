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

import abc
import json
import logging
import os
import pathlib
import re

from spl2_testing_framework.tools.results import Metrics, Results
from spl2_testing_framework.tools.test_types import (
    BoxTest,
    SingleSPL2,
    TestSuite,
    UnitTest,
)

_LOGGER = logging.getLogger(__name__)


class SamplesNotFoundException(Exception):
    """An Exception to be raised if samples are not found"""

    pass


class TestDiscovery(abc.ABC):
    """Base class for test discovery classes"""

    def __init__(self, path: str, performance_check: str):
        self.path = pathlib.Path(path)
        self._performance_check = performance_check
        self.tests = TestSuite()

    def _read_tests(self, test_name: str) -> None:
        tests_paths = self.path.rglob(test_name)
        self._raw_tests = {
            x: pathlib.Path(x).read_text(encoding="utf-8") for x in tests_paths
        }


class BoxTestDiscovery(TestDiscovery):
    """Discovers tests for box tests, looking into module.test.json files"""

    def __init__(self, path: str, performance_check: str):
        super().__init__(path, performance_check)

    def discover_tests(self) -> None:
        self._read_tests("module.test.json")
        self._parse_tests()

    def _parse_tests(self) -> None:
        self._parsed_modules = {
            x: json.loads(content) for x, content in self._raw_tests.items()
        }

        for module_path, content in self._parsed_modules.items():
            path = module_path.parent
            for test in content:
                name = test["filename"].replace(".spl2", "")
                test_input = test["test"]["source"]
                code_module_path = path / test["filename"]
                output = [
                    Results(x)
                    for x in test["test"].get("expected_destination_result", [])
                ]
                metrics = [
                    Metrics(x)
                    for x in test["test"].get("expected_metrics_destination_result", [])
                ]
                test = BoxTest(
                    name=name,
                    input=test_input,
                    output=output,
                    metrics=metrics,
                    module_path=module_path,
                    code_module_path=code_module_path,
                )
                test.meta["performance"] = self._performance_check
                self.tests.add(test)


class SingleSPL2Discovery(TestDiscovery):
    """Discovers the template file and its samples"""

    def __init__(
        self,
        path: str,
        template_file,
        sample_file=None,
        sample_delimiter="\n",
        performance_check="no",
    ):
        super().__init__(path, performance_check)
        self.template_file = template_file
        self.sample_file = sample_file
        self.sample_delimiter = sample_delimiter

    def discover_tests(self) -> None:
        if not self.sample_file:
            self._read_tests("module.json")
        self._parse_tests()

    def _parse_tests(self) -> None:
        name = None
        code_module_path = None
        if self.sample_file:
            _LOGGER.info("Reading samples from provided sample file.")
            events = self._read_samples_from_file(delimiter=self.sample_delimiter)
            name = self.template_file.replace(".spl2", "")
            code_module_path = next(self.path.rglob(self.template_file), None)
        else:
            _LOGGER.info("Reading samples from corresponding module.json file")
            self._parsed_modules = {
                x: json.loads(content) for x, content in self._raw_tests.items()
            }
            events = None
            for module_path, content in self._parsed_modules.items():
                path = module_path.parent
                break_outer = False
                for test in content:
                    if test["filename"] == os.path.basename(self.template_file):
                        name = test["filename"].replace(".spl2", "")
                        code_module_path = path / test["filename"]
                        events = test["context"]["events"]
                        if isinstance(events, str):
                            events = events.split("\r\n")
                        elif isinstance(events, list):
                            events = [event["_raw"] for event in events]
                        else:
                            _LOGGER.error("Invalid events found.")
                            raise SamplesNotFoundException(
                                "No valid sample events found. Exiting.."
                            )
                        break_outer = True
                        break
                if break_outer:
                    break
        if not events:
            _LOGGER.error("No events found.")
            raise SamplesNotFoundException("No valid sample events found. Exiting..")
        _LOGGER.debug(f"Events collected: {events}")
        test_input = self._parse_and_append_events(events)

        test = SingleSPL2(
            name=name,
            input=test_input,
            code_module_path=code_module_path,
        )
        test.meta["performance"] = self._performance_check

        self.tests.add(test)

    def _read_samples_from_file(self, delimiter):
        with open(self.sample_file) as file:
            events = filter(lambda ev: len(ev) > 0, file.read().split(delimiter))
            updated_events = []
            for event in events:
                event = "".join([delimiter, event])
                updated_events.append(event)
            final_events = [
                event.encode().decode("unicode_escape") for event in updated_events
            ]
        return final_events

    def _parse_and_append_events(self, events):
        formatted_events = ",".join(
            [f"{{_raw: {json.dumps(event)} }}" for event in events]
        )
        template_module = f"[{formatted_events}]"
        return template_module


class UTDiscovery(TestDiscovery):
    """Discovers tests for unit tests, looking into .test.spl2 files"""

    def __init__(self, path: str):
        super().__init__(path, performance_check="no")

    def discover_tests(self) -> None:
        self._read_tests("*.test.spl2")
        self._parse_tests()

    def _parse_tests(self) -> None:
        self.parsed = {
            filename: re.findall(r"\$?(.*?__test)", test_file_content)
            for filename, test_file_content in self._raw_tests.items()
        }

        for file, tests in self.parsed.items():
            path = pathlib.Path(file)
            file_name = path.name
            content = path.read_text(encoding="utf-8")
            code_module_name = file_name.replace(".test.", ".")
            code_module_path = path.parent / code_module_name

            for test in tests:
                self.tests.add(
                    UnitTest(
                        name=test,
                        file_name=file_name,
                        file_path=path,
                        content=content,
                        code_module_path=code_module_path,
                    )
                )
