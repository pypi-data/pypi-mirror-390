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
from collections import UserDict
from datetime import datetime, timezone
from os import remove
from typing import Any
import pytest


class Results(UserDict):
    _ignore_empty_strings = False
    """Class responsible for parsing and storing results from Splunk, IP and CLI.
    It's necessary to parse nested jsons and other python types to strings in order to compare them
    """

    def __init__(self, dictionary: dict = None, **kwargs):
        super().__init__(dictionary, **kwargs)
        self.data = self._cast_types(self.data)
        self.data = self._remove_all_string_nulls_from_dicts(
            self.data
        )  # TODO -> remove

        self._remove_timestamps_if_necessary()
        self._remove_all_empty_strings_from_dicts_if_necessary()

    @staticmethod
    def _cast_types(data: Any):
        """Casts everything into dicts / lists / strings.
        This is necessary because Splunk, IP and CLI often return different types of data.
        """
        if isinstance(data, str) and (data.startswith("[") or data.startswith("{")):
            try:
                data = json.loads(data)
            except Exception:
                pass  # If it fails, it's not a json, so it's just a normal string

        if isinstance(data, list):
            data = [Results._cast_types(item) for item in data]
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = Results._cast_types(value)
                if key == "_time":
                    data[key] = Results._convert_timestamp(value)
        if isinstance(data, (int, float)):
            data = str(data)

        return data

    @staticmethod
    def _convert_timestamp(timestamp):
        """We need to convert timestamp, as there are different formats returned by cloud / CLI / splunk"""
        try:
            ts = datetime.fromisoformat(timestamp)
        except ValueError:
            ts = datetime.fromtimestamp(float(timestamp), timezone.utc)

        return ts.isoformat()

    def __hash__(self):
        return hash(json.dumps(self.data, sort_keys=True))

    def _remove_timestamps_if_necessary(self):
        """Compatibility workaround
        Because IP is adding _has_time field and automatically adds timestamp=now() if there is no timestamp,
        but CLI doesn't, we need to remove it from comparison.
        """

        if self.data.get("_has_time", "1") == "0":
            self.data.pop("_has_time", None)
            self.data.pop("_time", None)
        else:
            self.data.pop("_has_time", None)

    @staticmethod
    def _remove_field_by_value(data, value):
        # TODO -> remove, it's just a workaround for different behaviour of splunk, IP and CLI
        """Because of different behaviour of Splunk, IP and CLI, we need to remove all "null" values,
        which are returned by CLI
        """
        for k, v in list(
            data.items()
        ):  # list(...) is to avoid changing dict size during iteration
            if v == value:
                del data[k]
            if isinstance(v, dict):
                Results._remove_field_by_value(v, value)
            if isinstance(v, list):
                for item in v[:]:
                    if isinstance(item, dict):
                        Results._remove_field_by_value(item, value)

        return data

    def _remove_all_string_nulls_from_dicts(self, data):
        # TODO -> remove, it's just a workaround for different behaviour of splunk, IP and CLI
        """Because of different behaviour of Splunk, IP and CLI, we need to remove all "null" values,
        which are returned by CLI
        """
        return self._remove_field_by_value(data, "null")

    def _remove_all_empty_strings_from_dicts_if_necessary(self):
        """If ignore_empty_strings is True, remove all empty strings from dicts
        This is necessary because for some cases we may want to ignore empty strings in comparison
        (e.g. when a field is not set, it may be returned as empty string)
        """
        if self._ignore_empty_strings:
            self.data = self._remove_field_by_value(self.data, "")

    def __lt__(self, other):
        if "_raw" in self.data:
            s = self.data.get("_raw")
            o = other.data.get("_raw")
        else:
            s = self.data.get("name")  # just a "workaround" for log_to_metrics func
            o = other.data.get("name")
        return json.dumps(s, sort_keys=True) < json.dumps(o, sort_keys=True)


class Metrics(Results):
    """Class responsible for storing metrics from Splunk, IP and CLI.
    Its main responsibility is to remove  metric_ prefix from keys in order to compare
    actual metric results with expected ones.
    """

    def __init__(self, dictionary: dict = None, **kwargs):
        if not dictionary:
            dictionary = {}
        modified_dict = self._remove_metric_prefix(dictionary)
        super().__init__(modified_dict, **kwargs)

    @staticmethod
    def _remove_metric_prefix(dictionary: dict = None):
        new_data = {}
        for key, value in dictionary.items():
            if key.startswith("metric_"):
                new_key = key[7:]
                new_data[new_key] = value
        return new_data
