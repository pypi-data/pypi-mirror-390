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

import logging

from tabulate import tabulate

from spl2_testing_framework.tools.performance import PerformanceCheck
from spl2_testing_framework.tools.test_types import UnitTest, BoxTest, SingleSPL2
from spl2_testing_framework.tools.utils import _make_functions_visible_for_testing
from spl2_testing_framework.tools.create_diff_sheet import ComparisonSheet


_LOGGER = logging.getLogger(__name__)


class SPL2TestRunner:
    """Main class responsible for running tests"""

    def __init__(self, search_client, run_configurations):
        self._search_client = search_client
        self.create_comparison_sheet = run_configurations.get("create_comparison_sheet")
        self.comp_obj = ComparisonSheet()

    def run_single_spl2_file(self, single_spl2_file: SingleSPL2) -> None:
        """Run a single spl2 file and print the output"""
        code_to_test = _make_functions_visible_for_testing(
            single_spl2_file.code_module_path
        )
        perf = PerformanceCheck(single_spl2_file)
        code_to_test = perf.apply_code_transformations(code_to_test)

        job = self._search_client.create_simple_job(
            single_spl2_file.input,
            single_spl2_file.code_module_path.stem,
            code_to_test,
            single_spl2_file.name,
        )
        self._search_client.run_job(job)
        job_result = self._search_client.get_job_results(job)
        output_result = job_result.get("destination", [])

        perf.check_performance(output_result)

        self.print_results(output_result, "RESULTS")
        metrics_result = job_result.get("metrics_destination", [])
        if len(metrics_result) > 0:
            self.print_results(metrics_result, "METRICS RESULTS")

    def print_results(self, results, type):
        """Prints the results in cli and log file"""
        separator = "#"
        _LOGGER.info(f"\n\n{separator * 50} {type} {separator * 50}\n\n")
        for item in results:
            table = tabulate(item.items(), headers=["Field", "Value"], tablefmt="plain")
            _LOGGER.info("\n" + "-" * 20 + "\n")
            _LOGGER.info("\n" + table + "\n")
            _LOGGER.info("\n" + "-" * 20 + "\n")

    def run_unit_test(self, template_test: UnitTest) -> None:
        """Run a unit test"""
        code_to_test = _make_functions_visible_for_testing(
            template_test.code_module_path
        )

        job = self._search_client.create_job(
            template_test.content,
            template_test.code_module_path.stem,
            code_to_test,
            template_test.name,
        )

        self._search_client.run_job(job)
        job_results = self._search_client.get_job_results(job)

        errors = []

        for result in job_results[template_test.name]:
            for case_result in result["_testResults"]["results"]:
                received, expected = (
                    case_result.get("received", None),
                    case_result.get("expected", None),
                )
                _LOGGER.debug("Check details: %s", case_result)

                if expected == received:
                    _LOGGER.info(
                        f'Check passed: {template_test.file_name}/{template_test.name}/{case_result["test"]}'
                    )
                else:
                    errors.append(
                        {
                            "TEST_STATEMENT": case_result["test"],
                            "ACTUAL": received,
                            "EXPECTED": expected,
                        }
                    )

        assert errors == [], f"Assertion errors: \n{errors}"

    def run_box_test(self, box_test: BoxTest) -> None:
        """Run a box test"""
        code_to_test = _make_functions_visible_for_testing(box_test.code_module_path)

        perf = PerformanceCheck(box_test)
        code_to_test = perf.apply_code_transformations(code_to_test)

        job = self._search_client.create_simple_job(
            box_test.input, box_test.code_module_path.stem, code_to_test, box_test.name
        )

        self._search_client.run_job(job)
        job_result = self._search_client.get_job_results(job)

        output_result = job_result.get("destination", [])
        metrics_result = job_result.get("metrics_destination", [])

        perf.check_performance(output_result)

        if box_test.output:
            if self.create_comparison_sheet:
                self.comp_obj.create_comparison_sheet(output_result, box_test)
            assert sorted(output_result) == sorted(box_test.output)
            _LOGGER.info(f"Output check passed: {box_test.name}")
            _LOGGER.debug("Received: \n%s", str(output_result))
            _LOGGER.debug("Expected: \n%s", str(box_test.output))
        else:
            _LOGGER.info(f"Output check skipped (expected empty): {box_test.name}")

        if box_test.metrics:
            assert sorted(metrics_result) == sorted(box_test.metrics)
            _LOGGER.info(f"Metric check passed: {box_test.name}")
            _LOGGER.debug("Received: \n%s", str(metrics_result))
            _LOGGER.debug("Expected: \n%s", str(box_test.metrics))
        else:
            _LOGGER.info(f"Metric check skipped (expected empty): {box_test.name}")
