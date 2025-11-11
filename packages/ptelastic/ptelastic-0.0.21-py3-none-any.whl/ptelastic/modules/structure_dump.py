"""
Elasticsearch data structure test

Contains:
- StrucDump to perform the data structure test
- run() function as an entry point for running the test
"""

import http
from http.client import responses
from mimetypes import inited

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint
import json

__TESTLABEL__ = "Elasticsearch data structure test"


class StrucDump:
    """
    This class gets all indices from an ES instance and then dumps what fields each index contains
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object, kbn: bool) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.kbn = kbn

        self.helpers.print_header(__TESTLABEL__)


    def _get_fields(self, mapping, prefix="") -> list:
        """
        This method recursively collects all field paths from ES mapping.

        :return: List of fields in an index mapping
        """
        fields = []
        props = mapping.get("properties", {})

        for field_name, field_info in props.items():
            full_name = f"{prefix}{field_name}" if not prefix else f"{prefix}.{field_name}"
            fields.append(full_name)

            if "properties" in field_info:
                fields.extend(self._get_fields(field_info, prefix=full_name))

        return fields


    def run(self) -> None:
        """
        Executes the Elasticsearch data structure test

        This method gets all indices with the helpers get_indices() method and then prints fields in an index by sending a request to
        the /<index name> endpoint and then retrieving all the fields with the method _get_fields()

        If the -vv/--verbose switch is provided, the method prints hidden indices (indices starting with .) along all other indices.

        The method adds the retrieved mapping to the JSON output
        """
        printed = False

        indices = self.helpers.get_indices(self.http_client, self.args.url, self.kbn, self.args.headers)

        for index in indices:
            if not self.args.built_in and index.startswith("."):
                continue

            request = self.helpers.KbnUrlParser(self.args.url, index, "GET", self.kbn)
            response = self.http_client.send_request(url=request.url, method=request.method, headers=self.args.headers)

            try:
                json_status = response.json().get("status", 200)
            except ValueError:
                json_status = 200

            if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK:
                ptprint(f"Error fetching index {index}. Received response: {response.status_code} {json.dumps(response.json(), indent=4)}",
                        "ADDITIONS",
                        self.args.verbose, indent=4, colortext=True)
                continue

            if not self.helpers.check_json(self.base_response):
                return

            response = response.json()

            try:
                fields = self._get_fields(mapping=response[index]["mappings"])
            except KeyError as e:
                ptprint(f"Index {index} has no mappings with {e} field", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
                continue

            index_properties = {"name": index,
                                "mappings": response.get(index, {}).get("mappings", {})}
            mapping_node = self.ptjsonlib.create_node_object("indexStructure", properties=index_properties)
            self.ptjsonlib.add_node(mapping_node)

            ptprint(f"Index {index}", "VULN", not self.args.json, indent=4)
            ptprint(', '.join(fields), "VULN", not self.args.json, indent=8)
            printed = True

        if not printed:
            ptprint("Could not find any non built-in indices", "INFO", not self.args.json, indent=4)

def run(args, ptjsonlib, helpers, http_client, base_response, kbn=False):
    """Entry point for running the StrucDump test"""
    StrucDump(args, ptjsonlib, helpers, http_client, base_response, kbn).run()
