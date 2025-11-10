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

import json
import os

import pytest

from .tools.results import Results

pytest.register_assert_rewrite("spl2_testing_framework")

from requests.auth import AuthBase, HTTPBasicAuth

from spl2_testing_framework.tools.search_clients.cli_search_client import (
    CLISearchClient,
)
from spl2_testing_framework.tools.search_clients.cloud_search_client import (
    CloudSearchClient,
)
from spl2_testing_framework.tools.search_clients.splunk_search_client import (
    SplunkSearchClient,
)
from spl2_testing_framework.tools.spl2test_runner import SPL2TestRunner
from spl2_testing_framework.tools.test_discovery import (
    BoxTestDiscovery,
    SamplesNotFoundException,
    SingleSPL2Discovery,
    UTDiscovery,
)

UNIT_TEST = "unit_test"
BOX_TEST = "box_test"
SINGLE_SPL2_FILE = "single_spl2_file"

IGNORE_EMPTY_STRINGS = "ignore_empty_strings"
CREATE_COMPARISON_SHEET = "create_comparison_sheet"
PERFORMANCE_CHECK = "performance_check"
TEST_TYPE = "type"
TEST_DIR = "test_dir"

import logging

from .logger_manager import setup_logging

setup_logging()

_LOGGER = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(f"--{TEST_TYPE}", action="store", default="local")
    parser.addoption(f"--{TEST_DIR}", action="store", default=".")
    parser.addoption(
        f"--{PERFORMANCE_CHECK}",
        action="store",
        default="no",
        choices=["no", "time", "detailed_time"],
    )
    parser.addoption("--template_file", action="store", default=None)
    parser.addoption("--sample_file", action="store", default=None)
    parser.addoption("--sample_delimiter", action="store", default="\n")
    parser.addoption(f"--{CREATE_COMPARISON_SHEET}", action="store_true", default=False)
    parser.addoption(f"--{IGNORE_EMPTY_STRINGS}", action="store_true")


def pytest_generate_tests(metafunc):
    """This function is used for dynamic generation of tests based on the test files in the directory specified by the
    --test_dir option"""
    test_dir = metafunc.config.getoption(TEST_DIR)
    performance_check = metafunc.config.getoption(PERFORMANCE_CHECK)
    _set_results_options(metafunc)

    if BOX_TEST in metafunc.fixturenames:
        _LOGGER.info("Collecting Box Tests")
        module_tests = BoxTestDiscovery(test_dir, performance_check)
        module_tests.discover_tests()
        metafunc.parametrize(
            "%s" % BOX_TEST, module_tests.tests, ids=module_tests.tests.get_ids()
        )

    if SINGLE_SPL2_FILE in metafunc.fixturenames:
        _LOGGER.info("Collecting the single spl2 file")
        template_file = metafunc.config.getoption("template_file")
        if template_file is None:
            pytest.skip("No template file found to execute. Exiting..")
        sample_file = metafunc.config.getoption("sample_file")
        sample_delimiter = metafunc.config.getoption("sample_delimiter")
        spl2_pipelines = SingleSPL2Discovery(
            test_dir,
            template_file,
            sample_file,
            sample_delimiter,
            performance_check=performance_check,
        )
        try:
            spl2_pipelines.discover_tests()
        except SamplesNotFoundException as err:
            pytest.exit(err)
        metafunc.parametrize(
            "%s" % SINGLE_SPL2_FILE,
            spl2_pipelines.tests,
            ids=spl2_pipelines.tests.get_ids(),
        )

    if UNIT_TEST in metafunc.fixturenames:
        _LOGGER.info("Collecting Unit Tests")
        unit_tests = UTDiscovery(test_dir)
        unit_tests.discover_tests()
        metafunc.parametrize(
            UNIT_TEST, unit_tests.tests, ids=unit_tests.tests.get_ids()
        )


@pytest.fixture(scope="session")
def spl2_test_runner(
    request,
    config,
    basic_authentication,
    bearer_token_authentication,
    run_configurations,
):
    """This fixture is used to create a test runner object based on the test type specified by the --type option
    3 types of tests are supported: 'splunk', 'cloud', 'cli'
    """
    test_type = request.config.getoption(TEST_TYPE).lower()
    if test_type == "splunk":
        url = f"{config['host']}:{config['port']}"
        search_client = SplunkSearchClient(url=url, auth=basic_authentication)
    elif test_type == "cli":
        search_client = CLISearchClient()
    elif test_type == "cloud":
        url = f"https://{config['tenant']}.api.{config['cloud_instance']}/{config['tenant']}"
        search_client = CloudSearchClient(url=url, auth=bearer_token_authentication)
    else:
        raise Exception(
            "Unknown test type: {}. Supported tests types: 'splunk', 'cloud', 'cli'".format(
                test_type
            )
        )

    x = SPL2TestRunner(search_client, run_configurations)
    return x


@pytest.fixture(scope="session")
def run_configurations(request):
    """Returns all the configuration options in one object (dict). Add more as necessary."""
    return {
        CREATE_COMPARISON_SHEET: request.config.getoption(
            f"--{CREATE_COMPARISON_SHEET}"
        ),
    }


@pytest.fixture(scope="session")
def config():
    """This fixture is used to read the configuration from the environment variables or from the spl2_test_config.json
    Configuration set using environment variables will be overwritten by settings from spl2_test_config.json file,
    however empty values in spl2_test_config.json will be ignored.
    """
    host = os.environ.get("SPL2_TF_HOST", None)
    port = os.environ.get("SPL2_TF_PORT", None)
    user = os.environ.get("SPL2_TF_USER", None)
    password = os.environ.get("SPL2_TF_PASSWORD", None)
    bearer_token = os.environ.get("SPL2_TF_BEARER_TOKEN", None)
    tenant = os.environ.get("SPL2_TF_TENANT", None)
    cloud_instance = os.environ.get("SPL2_TF_CLOUD_INSTANCE", None)

    try:
        with open("spl2_test_config.json", "rb") as f:
            conf_file = json.load(fp=f)
    except FileNotFoundError:
        from spl2_testing_framework.tools.utils import get_framework_root

        with open(f"{get_framework_root()}/spl2_test_config.json", "rb") as f:
            conf_file = json.load(fp=f)

    if conf_file.get("user", None):
        user = conf_file["user"]

    if conf_file.get("host", None):
        host = conf_file["host"]

    if conf_file.get("port", None):
        port = conf_file["port"]

    if conf_file.get("password", None):
        password = conf_file["password"]

    if conf_file.get("bearer_token", None):
        bearer_token = conf_file["bearer_token"]

    if conf_file.get("tenant", None):
        tenant = conf_file["tenant"]

    if conf_file.get("cloud_instance", None):
        cloud_instance = conf_file["cloud_instance"]

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "bearer_token": bearer_token,
        "tenant": tenant,
        "cloud_instance": cloud_instance,
    }


@pytest.fixture(scope="session")
def basic_authentication(config):
    return HTTPBasicAuth(config.get("user", ""), config.get("password", ""))


@pytest.fixture(scope="session")
def bearer_token_authentication(config):
    class HTTPBearerTokenAuth(AuthBase):
        """Attaches HTTP Basic Authentication to the given Request object."""

        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["Authorization"] = f"Bearer {self.token}"
            return r

    token = config.get("bearer_token", "")
    return HTTPBearerTokenAuth(token)


def _set_results_options(metafunc):
    ignore_empty_strings = metafunc.config.getoption(IGNORE_EMPTY_STRINGS)
    Results._ignore_empty_strings = ignore_empty_strings
