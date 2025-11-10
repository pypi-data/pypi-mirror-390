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

import json
import time
from typing import Dict, Union, List

import requests
from requests import Response

from ..jobs.job import Job
from ..results import Results, Metrics
from abc import ABC, abstractmethod


class SearchClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run_job(self, job: Job):
        pass

    @abstractmethod
    def get_job_results(self, job: Job) -> Dict[str, Results]:
        pass

    @staticmethod
    @abstractmethod
    def create_job(*args, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def create_simple_job(*args, **kwargs):
        pass

    @staticmethod
    def _cast_results(results: dict) -> Dict[str, List[Union[Results, Metrics]]]:
        """Cast results to Results / Metrics instances"""
        rs = {}
        for key, value in results.items():
            if key == "metrics_destination":
                rs[key] = [Metrics(x) for x in value]
            else:
                rs[key] = [Results(x) for x in value]

        return rs


class HTTPSSearchClient(SearchClient):
    """Base class for HTTP based search clients."""

    @property
    @abstractmethod
    def DISPATCH_SERVICE(self):
        pass

    @property
    @abstractmethod
    def JOBS_SERVICE(self):
        pass

    def __init__(self, url: str, auth=None):
        super().__init__()
        self._base_url = url
        self.auth = auth

    def run_job(self, job: Job) -> Response:
        """Run a job."""
        response = requests.post(
            self.dispatch_url,
            data=json.dumps(job.job_content),
            verify=False,
            auth=self.auth,
        )

        job._assign_ids_from_response(response)

        return response

    @property
    def url(self) -> str:
        """Base URL of a Splunk instance / cloud tenant."""
        return self._base_url

    @property
    def dispatch_url(self) -> str:
        """URL of the dispatch service."""
        return f"{self.url}/{self.DISPATCH_SERVICE}"

    @property
    def jobs_url(self) -> str:
        """URL of the job service."""
        return f"{self.url}/{self.JOBS_SERVICE}"

    def _get_job_details_url(self, job_id: str) -> str:
        return f"{self.jobs_url}/{job_id}"

    def get_job_results(self, job: Job) -> Dict[str, Union[Results, Metrics]]:
        """Get results of a job."""
        for job_name, job_id in job.ids.items():
            self._wait_for_job_status(job_id)

            job_url = self._get_job_results_url(job_id)

            response = requests.get(job_url, verify=False, auth=self.auth)
            while response.status_code == 204:
                time.sleep(1)
                response = requests.get(job_url, verify=False, auth=self.auth)
            if response.status_code != 200:
                raise Exception(response.status_code, response.content)

            job.result[job_name] = response.json()["results"]

        return self._cast_results(job.result)

    @staticmethod
    @abstractmethod
    def create_job(*args, **kwargs):
        pass
