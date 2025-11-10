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
import os
import re
from copy import copy
from datetime import datetime
from itertools import groupby
from typing import Tuple, List, Dict

from spl2_testing_framework.tools.test_types import Test

_LOGGER = logging.getLogger(__name__)


class PerformanceCheck:
    """
    Class responsible for adding timestamps and validating performance of SPL2 pipelines
    For basic usecase (_performance_check_type == "time") it's showing the time of spl2 pipeline execution
    For _performance_check_type == "detailed_time" it's printing pipeline code with added execution time for every
        line, which consists code statement. The result of "detailed_time" execution is also saved to the text file.
    """

    OUTPUT_DIR = "PERF_CHECK"
    PIPELINE_PATTERN = re.compile(
        r"(?P<fullmatch>"
        r"^\s*?\$pipeline\s*?=\s*?\|?\s*?from\s*?\$source\s*?"  # first line of pipeline
        r"(.|\n)*?"  # anything in between
        r"(\|\s*?into\s*?\$destination)"  # last line of pipeline definition
        r")",
        flags=re.M | re.VERBOSE,
    )

    FUNCTION_PATTERN = re.compile(
        r"^(?P<fullmatch>"
        r"(export\s+)?function\s+(?P<f_name>\S+)\((?P<source>\S+):"  # function header
        r".*{\n\s+return\s+(\|\s+)?from\s+(?P=source)\n*"  # return statement
        r"(?P<statements>(.|\n)*?)"  # anything before closing bracket
        r"(?P<closing_bracket>^\s*})"  # closing bracket [ASSUMED IT'S IN THE NEW LINE]
        r")",
        flags=re.M | re.VERBOSE,
    )

    STATEMENT_PATTERN = re.compile(r"^(?P<lx>\s*?\|.*)$", re.M)

    def __init__(self, test: Test):
        self._test = test
        self._performance_check_type = test.meta.get("performance", None)
        self.code_module = None

    def apply_code_transformations(self, code_module):
        """Apply code transformations necessary for measuring performance.
        Depending on perfromance_check_type (assigned to instance) it's adding code
        for calculating timestamps to spl2 pipeline"""
        if self._performance_check_type == "time":
            code_module = self._performance_time_of_execution_(code_module)
        elif self._performance_check_type == "detailed_time":
            code_module = self._performance_timestamps(code_module)

        self.code_module = code_module
        return code_module

    def check_performance(self, output_result):
        """Check performance basing on timestamps in the output.
        Depending on performance_check_type (assigned to instance) it's calculating time of execution
        of spl2 pipeline or injecting timestamp values into the pipeline code"""
        if self._performance_check_type == "time":
            return self._check_time_of_execution(output_result)
        elif self._performance_check_type == "detailed_time":
            return self._check_profiling(output_result)

    def _check_time_of_execution(self, output_result):
        """Log time of execution to stdout and cleanup results."""
        _LOGGER.info("Checking time of execution... ")

        for event_no, single_output in enumerate(output_result):
            time_of_execution = single_output.get("_timestamp_perf_exec", None)
            _LOGGER.info(
                f"Time of pipeline execution for event no {event_no}: {float(time_of_execution) * 1000}ms"
            )

        self._cleanup_result(output_result)

    @staticmethod
    def __find_group(timestamp):
        """Finds a group of timestamps basing on function name, as their name consists it"""
        m = re.search(r"_timestamp_(.+?)_\d{3}", timestamp[0])
        return m.group(1)

    @staticmethod
    def __calculate_diff_for_timestamps(timestamps: List[List]) -> List[Tuple]:
        """Calculate a time diff between consecutive timestamps and the relative"""
        diffs = []
        ts = sorted(
            timestamps, key=lambda x: x[0]
        )  # sort by name, to have the order correct
        time_of_func_exec = ts[-1][1] - ts[0][1]
        for start, end in zip(ts[:-1], ts[1:]):
            diff: float = end[1] - start[1]
            relative_time: float = diff / time_of_func_exec
            diffs.append((start[0], diff, relative_time))

        return diffs

    def _check_profiling(self, output_result: List[Dict[str, str]]) -> List:
        """Add timestamp values to pipeline code and cleanup results.
        Timestamps are modified to be relative to 0 - which is the start of the pipeline.
        """
        _LOGGER.info("Checking profiling results... ")
        outputs = []
        for event_no, single_output in enumerate(output_result):
            perf = [
                [field, float(value)]
                for field, value in single_output.items()
                if field.startswith("_timestamp_")
            ]

            calculated_diffs = []
            for _, v in groupby(perf, self.__find_group):
                calculated_diffs.extend(self.__calculate_diff_for_timestamps(list(v)))

            output = copy(self.code_module)

            for timestamp_name, value, relative in calculated_diffs:
                output = re.sub(
                    rf"\| eval {timestamp_name}=time\(\)",
                    f">>> {(value * 1000):.6f}ms [{relative:.2%}] <<< ",
                    output,
                )

            output = re.sub(r"\| eval _timestamp_\w+_\d{3}=time\(\)", r"", output)

            _LOGGER.info(output)

            self._save_output(output, event_no)
            outputs.append(output)

        self._cleanup_result(output_result)
        return outputs

    def _save_output(self, output: str, event_number: int) -> None:
        """Save output to text file"""
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        filename = f"{self.OUTPUT_DIR}/performance_{self._test.name}_{event_number}_{datetime.now()}.txt"

        with open(filename, "w") as f:
            f.write(output)

    @staticmethod
    def _cleanup_result(output_result: List) -> List:
        """Remove all timestamps from output not to brake assertions"""
        for single_result in output_result:
            for k in list(single_result.keys()):
                if k.startswith("_timestamp_perf"):
                    del single_result[k]

        return output_result

    @staticmethod
    def _performance_time_of_execution_(code_module: str) -> str:
        """Injects 3 timestamps to code - for beginning and end of pipeline execution
        and also the difference of these 2.
        """
        code_module = re.sub(
            r"(^\s*?\$pipeline\s*?=\s*?\|?\s*?from\s*?\$source\s*?)",
            r"\1 | eval _timestamp_perf_start=time()",
            code_module,
            flags=re.M,
        )

        code_module = re.sub(
            r"(\|\s*?into\s*?\$destination)",
            r"| eval _timestamp_perf_stop = time()"
            r"| eval _timestamp_perf_exec = _timestamp_perf_stop - _timestamp_perf_start \1",
            code_module,
            flags=re.M,
        )

        return code_module

    def _performance_timestamps(self, code_module: str) -> str:
        """Injects time of execution just before every command (In practise in every line which starts from "|")"""

        functions = self.__parse_functions(code_module)
        pipeline = self.__parse_pipeline(code_module)

        functions.append(pipeline)

        for f in functions:
            new_function = self.__add_timestamps_to_function(f)
            code_module = code_module.replace(f["fullmatch"], new_function)

        return code_module

    def __parse_functions(self, code_module: str) -> List[Dict]:
        """Parse all functions from code module. The finding contains groups necessary for parsing it
        and adding timestamps"""
        functions = [m.groupdict() for m in self.FUNCTION_PATTERN.finditer(code_module)]
        return functions

    def __parse_pipeline(self, code_module: str) -> Dict:
        """Parse pipeline definition from code module. The finding contains groups necessary for parsing it
        and adding timestamps"""
        pipeline = [m.groupdict() for m in self.PIPELINE_PATTERN.finditer(code_module)][
            0
        ]
        pipeline[
            "f_name"
        ] = "__main_pipeline__"  # just to make it working with function timestamp parser
        pipeline["closing_bracket"] = "NOTHING_THERE"  # ^^^

        return pipeline

    def __add_timestamps_to_function(self, f: Dict) -> str:
        """Add timestamps to all functions (and also correctly parsed pipeline definition)
        Timestamps are parametrized using function name and numbered consecutively"""
        new_function = self.STATEMENT_PATTERN.sub(
            rf"| eval _time_{f['f_name']}_placeholder=time() \g<lx>", f["fullmatch"]
        )

        new_function = re.sub(
            rf"^{f['closing_bracket']}",
            rf"| eval _time_{f['f_name']}_placeholder=time() {f['closing_bracket']}",
            new_function,
            flags=re.M,
        )

        func_timestamps = re.findall(rf"_time_{f['f_name']}_placeholder", new_function)

        for n, timestamp in enumerate(func_timestamps):
            new_function = re.sub(
                timestamp,
                rf"_timestamp_perf{f['f_name']}_{n:03d}",
                new_function,
                count=1,
            )

        return new_function
