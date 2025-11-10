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

from requests import Response

from ..utils import read_assertions_module, read_commands_modules


class Job:
    """A job that can be executed in the testing framework.
    Every pipeline that is tested in the framework is represented by a job,
    It contains tested code, test code, some helper code modules (assertions and commands)
    and job results"""

    def __init__(
        self,
        test_content: str,
        code_module_name: str,
        code_module_content: str,
        test_name: str,
    ):
        self._result = {}
        self._ids = {}
        self.assertions_module = read_assertions_module()
        self.commands_module = read_commands_modules()
        self.job_content = None

        self.test_module = f"import * from {code_module_name}\n{test_content}"
        self.code_module_name = code_module_name
        self.code_module_content = code_module_content
        self.test_name = test_name

    @property
    def ids(self) -> dict:
        """IDs of jobs run on the Splunk server, IP/EP or CLI"""
        return self._ids

    @ids.setter
    def ids(self, value: dict):
        self._ids = value

    def _assign_ids_from_response(self, response: Response):
        raise NotImplementedError()

    @property
    def result(self) -> dict:
        return self._result

    @result.setter
    def result(self, value: dict):
        """Results of jobs run on the Splunk server, IP/EP or CLI"""
        self._result = value
