"""
Elasticsearch data dump module

Contains:
- DataDump to perform the data dump
- run() function as an entry point for running the test
"""

import http
from http.client import responses
from mimetypes import inited
import json
from typing import Literal

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch data dump module"


class DataDump:
    """
    This class dumps all data from indices in an Elasticsearch instance
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object, kbn: bool) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.kbn = kbn

        self.helpers.print_header(__TESTLABEL__)


    def _get_data(self, data: dict, field: str):
        """
        This method retrieves the value assigned to the provided field in the index data
        """
        if "." in field:
            field = field.split(".")
            value = data
            for key in field:
                value = value[key]
        else:
            value = data[field]

        return value


    def _get_field(self, entry: dict) -> dict:
        """
        This method goes through all the fields provided with the -df/--dump-fields argument and retrieves its key:value pair from the data
        entry and then adds it to a dictionary that is returned by this method.

        :return: Dictionary with the desired fields and its values. Empty dictionary if the field/s is not found in the data entry
        """
        results = {"_id": entry["_id"], "_index": entry["_index"]}
        data = entry["_source"]

        for field in self.args.dump_field:
            try:
                results.update({field: self._get_data(data, field)})
            except KeyError as e:
                ptprint(f"The entry {entry} does not contain field {e}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

        return results if len(results.keys()) > 2 else {}


    def _write_to_file(self, data) -> None:
        with open(self.args.output, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def run(self) -> None:
        """
        Executes the Elasticsearch data dump

        This method sends an HTTP GET request to all the indices provided with the -di/--dump-index argument (all indices if none are provided)
        and dumps all data from it. If --df/--dump-fields are set, it extracts the desired fields from the data with the _get_field() method
        """
        full_data = []

        indices = self.args.dump_index or self.helpers.get_indices(self.http_client, self.args.url, self.kbn, self.args.headers)

        for index in indices:
            if not self.args.built_in and index.startswith("."):
                continue

            request = self.helpers.KbnUrlParser(self.args.url, f"{index}/_search?size=10000", "GET", self.kbn)
            response = self.http_client.send_request(url=request.url, method=request.method, headers=self.args.headers)

            try:
                json_status = response.json().get("status", 200)
            except ValueError:
                json_status = 200

            if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK or not self.helpers.check_json(response):
                ptprint(f"Error when reading indices: Received response: {response.status_code} {response.text}",
                        "ADDITIONS", not self.args.json, indent=4, colortext=True)
                continue

            data = response.json().get("hits", {}).get("hits", {})  # limit 10 000 hits

            if not data:
                ptprint(f"No data was returned for index {index}", "INFO", not self.args.json, indent=4)
                continue

            if self.args.dump_field:

                for entry in data:
                    isolated_data = self._get_field(entry)
                    ptprint(json.dumps(isolated_data, indent=4), "ADDITIONS", not self.args.json, indent=4) if isolated_data else None
                    full_data.append(isolated_data) if isolated_data else None

            else:
                ptprint(json.dumps(data, indent=4), "ADDITIONS", not self.args.json, indent=4)
                full_data.append(data) if data else None

        if self.args.output and full_data:
            self._write_to_file(full_data)


def run(args, ptjsonlib, helpers, http_client, base_response, kbn=False):
    """Entry point for running the DataDump test"""
    DataDump(args, ptjsonlib, helpers, http_client, base_response, kbn).run()
