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

import unittest
from unittest.mock import MagicMock
from requests import Response

from spl2_testing_framework.tools.jobs.cloud_job import CloudJob, CloudSimpleJob


class TestCloudJob(unittest.TestCase):
    def setUp(self):
        self.job = CloudJob(
            code_module_name="test_code_module",
            code_module_content="test_content",
            test_name="test_name",
            test_content="test_code",
        )

    def test_create_sets_job_content(self):
        self.job.create()
        self.assertIn("wipModules", self.job.job_content)
        self.assertIn("queryParameters", self.job.job_content)
        self.assertEqual(
            "import * from test_code_module\ntest_code", self.job.job_content["module"]
        )

    def test_assign_ids_from_response_success(self):
        response = MagicMock(spec=Response)
        response.ok = True
        response.json.return_value = {
            "queryParameters": {"test_name": {"sid": "12345"}}
        }
        self.job._assign_ids_from_response(response)
        self.assertEqual("12345", self.job.ids["test_name"])

    def test_assign_ids_from_response_failure(self):
        response = MagicMock(spec=Response)
        response.ok = False
        response.status_code = 400
        response.content = b"error"
        with self.assertRaises(Exception):
            self.job._assign_ids_from_response(response)

    def test_create_sets_query_details(self):
        self.job.create()
        defaults = self.job.job_content["queryParameters"]["defaults"]
        self.assertEqual(defaults["earliest"], "-30m@m")
        self.assertEqual(defaults["latest"], "now")
        self.assertEqual(defaults["profile"], "ingestProcessor")
        self.assertEqual(defaults["runtime"], "ingest.preview")
        self.assertTrue(defaults["collectFieldSummary"])
        self.assertTrue(defaults["collectTimeBuckets"])
        self.assertEqual(defaults["extractFields"], "all")
        self.assertTrue(defaults["enablePreview"])
        self.assertFalse(defaults["allowSideEffects"])


class TestCloudSimpleJob(unittest.TestCase):
    def setUp(self):
        self.job = CloudSimpleJob(
            source="src",
            code_module_name="mod",
            code_module_content="code",
            test_name="pipeline",
        )

    def test_create_sets_job_content(self):
        self.job.create()
        self.assertIn("wipModules", self.job.job_content)
        self.assertIn("queryParameters", self.job.job_content)
        self.assertEqual("shared.pipelines", self.job.job_content["namespace"])

    def test_assign_ids_from_response_success(self):
        response = MagicMock(spec=Response)
        response.ok = True
        response.json.return_value = {
            "queryParameters": {
                "destination": {"sid": "dest123"},
                "metrics_destination": {"sid": "met123"},
            }
        }
        self.job._assign_ids_from_response(response)
        self.assertEqual("dest123", self.job.ids["destination"])
        self.assertEqual("met123", self.job.ids["metrics_destination"])

    def test_assign_ids_from_response_missing_keys(self):
        response = MagicMock(spec=Response)
        response.ok = True
        response.json.return_value = {"queryParameters": {}}
        # Should not raise
        self.job._assign_ids_from_response(response)

    def test_assign_ids_from_response_failure(self):
        response = MagicMock(spec=Response)
        response.ok = False
        response.status_code = 500
        response.content = b"fail"
        with self.assertRaises(Exception):
            self.job._assign_ids_from_response(response)
