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


class CloudBaseJob(Job):
    @property
    def _query_details(self) -> dict:
        return {
            "earliest": "-30m@m",
            "latest": "now",
            "profile": "ingestProcessor",
            "runtime": "ingest.preview",
            "collectFieldSummary": True,
            "collectTimeBuckets": True,
            "extractFields": "all",
            "enablePreview": True,
            "allowSideEffects": False,
        }


class CloudJob(CloudBaseJob):
    """A job that is executed on the cloud tenant in unit tests."""

    def create(self):
        """Creates a job. To run the job use run_job() method."""
        self.job_content = {
            "wipModules": {
                "gdi.addons.spl2_content.dmx_utilities.assertions": {
                    "name": "assertions",
                    "definition": str(self.assertions_module),
                    "namespace": "/gdi.addons.spl2_content.dmx_utilities.assertions",
                },
                self.code_module_name: {
                    "name": self.code_module_name,
                    "definition": str(self.code_module_content),
                },
            },
            "module": self.test_module,
            "namespace": "",
            "queryParameters": {
                "defaults": self._query_details,
                self.test_name: {"saveAllResults": True},
            },
        }

        return self

    def _assign_ids_from_response(self, response: Response, metrics=False) -> None:
        if not response.ok:
            raise Exception(response.status_code, response.content)

        self.ids[self.test_name] = response.json()["queryParameters"][self.test_name][
            "sid"
        ]


class CloudSimpleJob(CloudBaseJob):
    """A job that is executed on the cloud tenant in box tests."""

    def __init__(
        self, source: str, code_module_name: str, code_module_content, test_name
    ):
        code_module_content += f"\n$source = from {str(source)};"
        super().__init__("", code_module_name, code_module_content, test_name)

    def create(self) -> "CloudSimpleJob":
        """Creates a job. To run the job use run_job() method."""
        self.job_content = {
            "wipModules": {},
            "module": self.code_module_content,
            "namespace": "shared.pipelines",
            "queryParameters": {
                "defaults": self._query_details,
                "pipeline": {"saveAllResults": False},
            },
        }

        return self

    def _assign_ids_from_response(self, response: Response, metrics=False) -> None:
        if not response.ok:
            raise Exception(response.status_code, response.content)

        for metric in ["destination", "metrics_destination"]:
            try:
                self.ids[metric] = response.json()["queryParameters"][metric]["sid"]
            except KeyError:
                pass
