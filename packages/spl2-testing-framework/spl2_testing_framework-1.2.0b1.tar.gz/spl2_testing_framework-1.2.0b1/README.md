# SPL2 Testing Framework

## Overview

The **SPL2 Testing Framework** enables running SPL2 tests both locally ( or on any Splunk instance with SPL2
orchestrator), remotely (using external cloud environments) or using cli.

- **For Cloud**: It uses
  the Search Service API.
- **For Splunk**: It uses the Splunk Search API (with SPL2 support)
- **For cli** - it uses the internal spl2-processor-cli library. This option is not available for public usage, as
  spl2-processor-cli is a Splunk internal tool.

## Prerequisites

### 1. Install Python and Poetry

1. Ensure `python3.x` is available
2. Install testing framework:
    - Install `poetry` and execute the command `poetry install` to create a virtual environment and install required
      dependencies.
    - OR
    - Install the library using pip:
      `pip install spl2-testing-framework`

### 2. Set configuration. It may be done in spl2_test_config.json file or environment variables

Note: setting configuration is necessary for running tests using splunk or cloud environment.
For running tests using cli no configuration is required.
The only requirement is to have this library installed, as described below

#### spl2_test_config.json - local file present in the current working directory (the directory from where tests are executed)

##### Configuration for running tests using cloud search client (Ingest processor)

* `cloud_instance` - address of Cloud host where the tests can be executed
    - e.g.: `staging.scs.splunk.com`
* `tenant` - tenant to use for testing
    - e.g.: `spl2-content`
* `bearer_token` - token used for authentication. To obtain the token, go
  to: `https://console.[cloud_instance]/[tenant]/settings`

##### Configuration for running tests using splunk search client (Splunk instance)

* `host` - address of Splunk host where the tests can be executed
    - e.g.: `localhost` or `https://10.202.35.219`
* `port` - port of Splunk host where the tests can be executed
    - usually `8089`, but can be different
* `user` - user to authenticate
* `password` - password to authenticate

#### The same configuration can be done using environment variables(however, spl2_test_config.json has higher priority):

##### cloud search client

* `SPL2_TF_CLOUD_INSTANCE` => `cloud_instance`
* `SPL2_TF_TENANT` => `tenant`
* `SPL2_TF_BEARER_TOKEN` => `bearer_token`

##### splunk search client

* `SPL2_TF_HOST` => `host`
* `SPL2_TF_PORT` => `port`
* `SPL2_TF_USER` => `user`
* `SPL2_TF_PASSWORD` => `password`

### 3. Installing spl2-processor-cli (Splunk internal tool)

`spl2-processor-cli` can be installed using brew:

`brew install spl2-processor-cli`

Before installation, it may be necessary to authenticate to artifactory by running:

`okta-artifactory-login -t generic`

## Running tests

To run tests, execute the command:

`spl2_tests_run [cli|splunk|cloud]`

In the directory where the tests are located.
Test discovery is recursive, so it's possible to run tests even from the root directory of the project.

It is possible to pass more options to the command, which works also with pytest, e.g.:

* `-k "filter"` - to run only tests which name contains "filter"
* `-v[vv]` - to see more verbose output
* `-n [auto|<number>]` - to run tests in parallel
    - `auto` - to use all available cores,
    - `<number>` - to use specific number of cores
    - however, it's recommended to run tests in parallel on cli mostly, as running on splunk or cloud doesn't give
      significant performance improvement
* `-x` - to stop on first failure
* `-pdb` - to enter debugger on failure
* ... and much more, whatever is supported by pytest

Additionally, the following options are supported:

* `--ignore_empty_strings` - to ignore empty strings in the results
* `--create_comparison_sheet` - to create a comparison sheet in `comparison_box_test` folder using actual and expected outputs (works only when running box tests)

Note: The `pytest.ini.sample` file allows you to define command parameters. Just update the configurations, rename the
file by removing the `.sample` extension, and execute the command.

### Run tests in IDE [PyCharm]

It's also possible to run tests in PyCharm. To do this, it's necessary to set `Run Configurations`

Sample configuration which may be used:

* Run configuration
    - Type: `Python test`
    - Module: `spl2_testing_framework.test_runner`
    - Parameters:
      `--type [cli | splunk | cloud] --test_dir /tests/resources -o log_cli=true --log-cli-level=INFO --verbose`
    - If test dir is not specified, current working directory will be used
    - If necessary another pytest options can be added

Note: It's necessary to set "pytest" as default test runner in PyCharm settings

## Executing a spl2 file

This framework also supports executing a single spl2 file and prints the results in command line as well as a log file.
This will help developers to get the results of the spl2 pipeline as and when they are developing the pipeline.

It requires 3 additional parameters:

* --template_file
* --sample_file
* --sample_delimiter

It will execute the template_file provided in the `--template_file` parameter. It will read samples if `--sample_file`
parameter is provided and will separate the samples by using `--sample_delimiter`. If `--sample_file` is not provided,
then it will look for the samples in the respective `module.json` file corresponding to the template_file.

To run a single spl2 file, execute the command:

`single_spl2_file_run [cli|splunk|cloud]`

It is possible to pass more options to the command, which works also with pytest, e.g.:

* `--test_dir` - Path in which the template file and module.json are available. If not provided, it will look for the
  current directory for the template file and module.json file
* `--template_file` - The spl2 template file to execute
* `--sample_file` - A file containing all the samples required for the template file. If not provided, it will look for
  the samples in module.json file of the corresponding template file
* `--sample_delimiter` - Separator for separating the samples provided in the sample file. If not provided, it will use
  newline as a default separator.

* ... and much more, whatever is supported by pytest

Note: The `pytest.ini.sample` file allows you to define command parameters. Just update the configurations, rename the
file by removing the `.sample` extension, and execute the command.

### Performance check

It is possible to measure execution time of spl2 pipeline, or even do more advanced time checks using flag:

* `--performance_check=time` - to run basic time measurements - time of execution of spl2 pipeline will be printed to
  stdout
* `--performance_check=detailed_time` - to do more advanced time checks which injects more timestamps into spl2
  pipeline.

Running `detailed_time` check creates text file with spl2 pipeline code with injected timestamps after every
command ("|")
Content of this file will also be printed to stdout.

This checks can be applied only to box tests, as assertions which are used in unit tests may impact spl2 pipeline
performance. 