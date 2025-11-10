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


import json
import logging
import subprocess
from ..jobs.cli_job import CLIAssertionJob, CLISimpleJob
from ..jobs.job import Job
from .search_client import SearchClient

_LOGGER = logging.getLogger(__name__)


class CLISearchClient(SearchClient):
    """Search client responsible for running jobs on CLI."""

    jobs_dict = {}

    @staticmethod
    def create_job(
        test_module: str, code_file_name: str, code_to_test: str, test_statement: str
    ) -> Job:
        """Creates a job for unit test run."""
        return CLIAssertionJob(
            test_module, code_file_name, code_to_test, test_statement
        ).create()

    @staticmethod
    def create_simple_job(
        source: str, code_module_name: str, code_module_content, test_name
    ) -> Job:
        """Creates a job for box test run."""

        return CLISimpleJob(
            source, code_module_name, code_module_content, test_name
        ).create()

    def run_job(self, job):
        """Run a job on CLI."""
        result = subprocess.run(
            job.job_content["command"],
            input=job.job_content["input_data"],  # Pass data to stdin
            text=True,  # Encode input_data as string
            capture_output=True,
        )

        if result.stderr:
            raise RuntimeError(result.stderr)

        job.result = json.loads(result.stdout)
        return

    def get_job_results(self, job: Job) -> dict:
        """Get results of a job."""
        tmp = {  # remove job_ prefix
            k.replace("job_", ""): v for k, v in job.result.items()
        }  # TODO for python>3.9 use str.remove_prefix

        results = self._cast_results(tmp)
        return results
