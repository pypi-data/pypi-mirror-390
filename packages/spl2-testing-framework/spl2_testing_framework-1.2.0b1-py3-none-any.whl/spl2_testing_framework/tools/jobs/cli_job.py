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

from .job import Job


class CLIAssertionJob(Job):
    """A job that is executed on CLI in unit tests."""

    def create(self) -> "CLIAssertionJob":
        """Creates a job. To run the job use run_job() method."""

        cli = "spl2-processor-cli"
        command = [
            cli,
            "test",
            "-s",
            self.test_name,
        ]

        input_data = "\n\n".join(
            [
                (  # for assertion tests we don't add assertions module
                    self.assertions_module
                    if not self.code_module_name == "assertions"
                    else ""
                ),
                self.commands_module,
                self.code_module_content,
                self.test_module,
            ]
        )
        self.job_content = {"command": command, "input_data": input_data}
        return self


class CLISimpleJob(Job):
    """A job that is executed on CLI in box tests."""

    def __init__(
        self, source: str, code_module_name: str, code_module_content, test_name
    ):
        code_module_content += f"\n$source = from {str(source)};"
        super().__init__("", code_module_name, code_module_content, test_name)

    def create(self) -> "CLISimpleJob":
        """Creates a job. To run the job use run_job() method."""

        cli = "spl2-processor-cli"
        command = [cli, "test", "-s", "pipeline"]

        input_data = "\n\n".join(
            [
                self.commands_module,
                self.code_module_content,
            ]
        )
        self.job_content = {"command": command, "input_data": input_data}
        return self
