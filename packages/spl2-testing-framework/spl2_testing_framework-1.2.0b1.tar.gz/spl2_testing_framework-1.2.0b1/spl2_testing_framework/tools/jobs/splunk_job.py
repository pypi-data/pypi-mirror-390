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

from .job import Job


class SplunkAssertionJob(Job):
    """A job that is executed on the Splunk server in unit tests."""

    def create(self) -> "SplunkAssertionJob":
        """Creates a job. To run the job use run_job() method."""
        self.job_content = {
            "wipModules": {
                "assertions": {
                    "name": "assertions",
                    "definition": str(self.assertions_module),
                    "namespace": "/gdi.addons.spl2_content.dmx_utilities.assertions",
                },
                "commands": {
                    "name": "commands",
                    "definition": str(self.commands_module),
                    "namespace": "commands",
                },
                self.code_module_name: {
                    "name": self.code_module_name,
                    "definition": str(self.code_module_content),
                },
            },
            "module": self.test_module,
            "namespace": "",
            "queryParameters": {
                "defaults": {
                    "earliest": "-30m@m",
                    "latest": "now",
                    "profile": "ingestProcessor",
                    "collectFieldSummary": True,
                    "collectTimeBuckets": True,
                    "extractFields": "all",
                    "enablePreview": True,
                    "allowSideEffects": False,
                },
                self.test_name: {"saveAllResults": True},
            },
        }

        return self

    def _assign_ids_from_response(self, response: Response) -> None:
        if not response.ok:
            raise Exception(response.status_code, response.content)

        self.ids = {x["name"]: x["sid"] for x in response.json() if x["sid"]}


class SplunkSimpleJob(Job):
    """A job that is executed on the Splunk server in box tests."""

    def __init__(
        self, source: str, code_module_name: str, code_module_content, test_name
    ):
        code_module_content += f"\n$source = from {str(source)};"
        super().__init__("", code_module_name, code_module_content, test_name)

    def create(self) -> "SplunkSimpleJob":
        """Creates a job. To run the job use run_job() method."""
        self.job_content = {
            "wipModules": {
                "commands": {
                    "name": "commands",
                    "definition": str(self.commands_module),
                    "namespace": "commands",
                },
            },
            "module": self.code_module_content,
            "namespace": "",
            "queryParameters": {
                "defaults": {
                    "earliest": "-30m@m",
                    "latest": "now",
                    "profile": None,
                    "collectFieldSummary": True,
                    "collectTimeBuckets": True,
                    "extractFields": "all",
                    "enablePreview": True,
                    "allowSideEffects": False,
                },
                "pipeline": {"saveAllResults": False},
            },
        }

        return self

    def _assign_ids_from_response(self, response: Response, metrics=False) -> None:
        if not response.ok:
            raise Exception(response.status_code, response.content)

        self.ids = {x["name"]: x["sid"] for x in response.json() if x["sid"]}
