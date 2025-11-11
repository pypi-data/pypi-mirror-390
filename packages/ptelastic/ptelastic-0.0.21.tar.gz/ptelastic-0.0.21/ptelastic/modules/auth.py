"""
Elasticsearch authentication test

This module implements a test that checks if an Elasticsearch instance has authentication enabled or disabled

Contains:
- Auth class for performing authentication test
- run() function as an entry point for running the test
"""

import http
from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint
from http import HTTPStatus

__TESTLABEL__ = "Elasticsearch authentication test"


class Auth:
    """
    This class tests to see if an Elasticsearch instance is running with authentication enabled or disabled by
    sending a GET request to the provided URL and looking at the HTTP response code.
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object, kbn: bool) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.kbn = kbn
        self.helpers.print_header(__TESTLABEL__)



    def _print_anon_role(self):
        """
        This method prints the role of the anonymous user (if any)
        """
        request = self.helpers.KbnUrlParser(self.args.url, "_security/user", "GET", self.kbn)
        response = self.http_client.send_request(request.url , method=request.method, headers=self.args.headers, allow_redirects=False)

        if not self.helpers.check_json:
            return

        json_status = response.json().get("status", 200)

        if response.status_code != http.HTTPStatus.OK or json_status != HTTPStatus.OK:
            ptprint(f"Error when probing authentication at {request.url}. Received response: {response.text}", "ERROR",
                    not self.args.json, indent=4)
            return

        users = response.json()

        for user in users.keys():
            if "anon" in user or "anonymous" in user:
                ptprint(f"Authentication is enabled, but anonymous access is allowed", "VULN", not self.args.json,
                        indent=4)
                ptprint(f"Anonymous role: {', '.join(users[user]['roles'])}", "VULN", not self.args.json, indent=8)
                return

        ptprint(f"Authentication is enabled. Anonymous access is not available", "OK", not self.args.json, indent=4)
        ptprint(f"Could not find username which would match 'anonymous' or 'anon'. All users: {','.join(users.keys())}",
                "OK", not self.args.json, indent=4)

    def _test_anon_auth(self) -> None:
        """
        This method checks to see if authentication is truly disabled or anonymous access is allowed
        """
        request = self.helpers.KbnUrlParser(self.args.url, "_xpack?filter_path=features.security", "GET", self.kbn)
        response = self.http_client.send_request(request.url , method=request.method, headers=self.args.headers, allow_redirects=False)

        if not self.helpers.check_json(response):
            return

        json_status = response.json().get("status", 200)

        if response.status_code != http.HTTPStatus.OK or json_status != HTTPStatus.OK:
            ptprint(f"Error when probing authentication at {request.url}. Received response: {response.status_code}",
                    "ERROR", not self.args.json, indent=4)
            return

        security = response.json()

        if not security.get("features", {}).get("security", {}).get("enabled", {}):
            ptprint(f"Authentication is disabled", "VULN", not self.args.json, indent=4)
            self.ptjsonlib.add_vulnerability("PTV-WEB-ELASTIC-AUTH")
            self.ptjsonlib.add_properties({"authentication": "disabled"})
            return

        self._print_anon_role()

    def run(self) -> None:
        """
        Executes the Elasticsearch authentication test

        Sends one HTTP GET request to the provided URL and determines if authentication is enabled or not by the
        HTTP response codes as follows:

        401 Unauthorized = Authentication is enabled
        200 OK - Authentication is disabled

        If authentication is disabled, a vulnerability and a property are added to the JSON result
        """
        response = self.base_response

        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            ptprint(f"Authentication is enabled", "OK", not self.args.json, indent=4)

        elif response.status_code == http.HTTPStatus.OK:
            self._test_anon_auth()

        else:
            ptprint(f"Webpage returns status code: {response.status_code}", "OK", not self.args.json, indent=4)


def run(args, ptjsonlib, helpers, http_client, base_response, kbn=False):
    """Entry point for running the Auth test"""
    Auth(args, ptjsonlib, helpers, http_client, base_response, kbn).run()
