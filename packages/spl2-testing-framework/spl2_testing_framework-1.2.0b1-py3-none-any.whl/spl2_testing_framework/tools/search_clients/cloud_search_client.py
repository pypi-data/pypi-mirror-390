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

#
#

import time
import requests
from requests import Response

from ..jobs.job import Job
from ..jobs.cloud_job import CloudJob, CloudSimpleJob
from .search_client import HTTPSSearchClient


class CloudSearchClient(HTTPSSearchClient):
    """Search client responsible for running jobs on cloud tenant."""

    DISPATCH_SERVICE = "search/v3alpha1/dispatch"
    JOBS_SERVICE = "search/v3alpha1/jobs"

    def _get_job_results_url(self, job_id: str) -> str:
        return f"{self.jobs_url}/{job_id}/results"

    @staticmethod
    def create_job(
        test_module: str, code_file_name: str, code_to_test: str, test_statement: str
    ) -> Job:
        """Creates a job for unit test run."""
        return CloudJob(
            test_module, code_file_name, code_to_test, test_statement
        ).create()

    @staticmethod
    def create_simple_job(
        source: str, code_module_name: str, code_module_content, test_name
    ) -> Job:
        """Creates a job for box test run."""
        return CloudSimpleJob(
            source, code_module_name, code_module_content, test_name
        ).create()

    def _wait_for_job_status(self, job_id: str) -> Response:
        time.sleep(2)

        while True:
            response = requests.get(
                self._get_job_details_url(job_id), verify=False, auth=self.auth
            )
            if response.status_code != 200:
                if "GET_PIPELINE_NOT_FOUND" in response.text:
                    continue
                raise Exception(f"Job failed, id: {job_id}", response.text)
            if response.json()["status"] == "failed":
                raise Exception(
                    f"Job failed, id: {job_id}", response.status_code, response.text
                )
            if response.json()["status"] == "done":
                return response
            time.sleep(1)
