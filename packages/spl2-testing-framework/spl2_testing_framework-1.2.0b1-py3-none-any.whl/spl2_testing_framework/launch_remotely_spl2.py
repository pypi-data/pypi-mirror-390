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
import json

from spl2_testing_framework.tools.modules_reader import get_template_file
from spl2_testing_framework.tools.payload_functions import create_pipeline_job
from spl2_testing_framework.tools.cloud_search_client import CloudSearchClient


class Spl2Runner:
    def _run_job_and_get_response(self, job):
        response = self._search_client.run_job(job)
        if response.status_code == 401:
            print(
                f"Unauthorised, may need to refresh token. Additional info: {response.text}"
            )
            exit(-1)
        if response.status_code != 201:
            print(f"Message: {response.text}. Status code: {response.status_code}.")
        return response

    def main(self):
        parser = argparse.ArgumentParser("spl2_launcher")
        parser.add_argument(
            "spl2file",
            help="Name of file to launch like: `pan_traffic_reduction.spl2`",
            type=str,
        )
        parser.add_argument(
            "-s",
            "--source",
            help="$source definition if it is not in the code.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-e", "--events", help="Events definition txt file.", type=str, default=None
        )
        args = parser.parse_args()
        self._search_client = CloudSearchClient()
        template_module = get_template_file(args.spl2file).read_text(encoding="utf-8")
        if args.source is not None:
            template_module = template_module + f"\n$source = from {args.source};"
        if args.events is not None:
            events = list(
                filter(lambda ev: len(ev) > 0, open(args.events).read().split("\n"))
            )
            template_module = template_module + f"\n$source = from ["
            for event in events:
                template_module = template_module + f"{{_raw: {json.dumps(event)} }}"
                if event != events[-1]:
                    template_module = template_module + ","
            template_module = template_module + "];"
        job = create_pipeline_job(
            template_module, "ingestProcessor", False, None
        )  # allways launch in IP profile to use IP runner for tests
        response = self._run_job_and_get_response(job)
        # TODO check both destinations
        destination_job_sid = response.json()["queryParameters"]["destination"]["sid"]

        self._search_client.wait_for_job_status(destination_job_sid)

        job_result = self._search_client.get_job_results(destination_job_sid)

        print(json.dumps(job_result, indent=2))


if __name__ == "__main__":
    spl2runner = Spl2Runner()
    spl2runner.main()
