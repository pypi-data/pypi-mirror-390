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
from ..jobs.splunk_job import SplunkAssertionJob, SplunkSimpleJob
from .search_client import HTTPSSearchClient


class SplunkSearchClient(HTTPSSearchClient):
    """Search client responsible for running jobs on Splunk instance"""

    DISPATCH_SERVICE = "servicesNS/admin/-/search/spl2-module-dispatch"
    JOBS_SERVICE = "servicesNS/admin/-/search/jobs"

    @staticmethod
    def create_job(
        test_module: str, code_file_name: str, code_to_test: str, test_statement: str
    ) -> Job:
        """Creates a job for unit test run."""
        return SplunkAssertionJob(
            test_module, code_file_name, code_to_test, test_statement
        ).create()

    @staticmethod
    def create_simple_job(
        source: str, code_module_name: str, code_module_content, test_name
    ) -> Job:
        """Creates a job for box test run."""
        return SplunkSimpleJob(
            source, code_module_name, code_module_content, test_name
        ).create()

    def _get_job_results_url(self, job_id: str) -> str:
        return f"{self.jobs_url}/{job_id}/results?output_mode=json"

    def _wait_for_job_status(self, job_id: str) -> Response:
        job_url = self._get_job_details_url(job_id)

        counter = 0
        while True:
            response = requests.get(job_url, verify=False, auth=self.auth)
            if response.status_code != 200:
                counter += 1
            if response.status_code == 200:
                return response
            time.sleep(1)
            if counter == 5:
                raise Exception(response.text)
