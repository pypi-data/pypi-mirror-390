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

import pathlib
import re
from functools import lru_cache


def get_framework_root() -> pathlib.Path:
    framework_root = pathlib.Path(__file__).parents[1]
    return framework_root


def _make_functions_visible_for_testing(code_module_path):
    code_module = code_module_path.read_text(encoding="utf-8")
    functions = re.findall(r"^function\s+([^(]+)\(", code_module, flags=re.M)
    for function in functions:
        if not re.search(r"export\s" + function, code_module):
            code_module = re.sub(
                r"^function\s+" + function,
                f"export function {function}",
                code_module,
                flags=re.M,
            )
    return code_module


@lru_cache(None)
def read_assertions_module():
    root_folder = get_framework_root()
    assertions_file = root_folder / "spl2_utils" / "assertions.spl2"
    return assertions_file.read_text(encoding="utf-8")


@lru_cache(None)
def read_commands_modules():
    root_folder = get_framework_root()
    commands_module = root_folder / "spl2_utils" / "logs_to_metrics.spl2"
    return commands_module.read_text(encoding="utf-8")
