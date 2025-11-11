"""
Elasticsearch software test

This module probes an Elasticsearch instance to see what kind of software it's running.
Specifically, it enumerates the Elasticsearch version, built-in modules and their version and plugins and their version

Contains:
- SwTest class for performing software enumeration
- run() function as an entry point for running the test
"""

import http
from http import HTTPStatus
from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch software test"


class SwTest:
    """
    This class probes the Elasticsearch host and finds out what kind of software it has running
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object, kbn: bool) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.kbn = kbn

        self.helpers.print_header(__TESTLABEL__)


    def _get_es_version(self) -> bool:
        """
        This method finds the Elasticsearch version by sending a GET request to http://<host>/ and looking at
        the returned JSON

        If successful, it adds the Elasticsearch version into the JSON output

        :return: False if we get an HTTP response other than 200 OK, or we don't find the version in the response.
                 True If we get an HTTP 200 OK response and we find the version
        """
        if not self.helpers.check_json(self.base_response):
            return False

        response = self.base_response

        if response.status_code != HTTPStatus.OK:
            ptprint(f"Could not enumerate ES version. Received response code: {response.status_code}",
                    "OK", not self.args.json, indent=4)
            return False

        response = response.json()
        es_properties = {"esVersion": response.get("version").get("number"),
                         "name": response.get("name"),
                         "clusterName": response.get("cluster_name"),
                         "apacheLuceneVersion": response.get("version").get("lucene_version")
                         }

        ptprint(f"Elasticsearch version: {es_properties['esVersion']}", "VULN", not self.args.json, indent=4)
        ptprint(f"Cluster name: {es_properties['clusterName']}", "VULN", not self.args.json, indent=4)
        ptprint(f"Apache Lucene Version: {es_properties['apacheLuceneVersion']}","VULN", not self.args.json, indent=4)
        node = self.ptjsonlib.create_node_object("swES", properties=es_properties)
        self.ptjsonlib.add_node(node)

        return True


    def _get_modules(self) -> bool:
        """
        This method enumerates the modules running on each Elasticsearch node by sending a GET request to
        http://<host>/_nodes and going through the JSON response

        If successful, it adds the module name, version and description into the JSON output

        :return: False if we get an HTTP response other than 200 OK. True if we get an HTTP 200 OK and we find modules
        """
        request = self.helpers.KbnUrlParser(self.args.url, "_nodes", "GET", self.kbn)
        response = self.http_client.send_request(request.url, method=request.method, headers=self.args.headers, allow_redirects=False)

        try:
            json_status = response.json().get("status", 200)
        except ValueError:
            json_status = 200

        if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK:
            ptprint(f"Could not enumerate modules", "OK",
                    not self.args.json, indent=4)
            ptprint(f"Received response code: {response.status_code}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return False

        response = response.json()
        nodes = response["nodes"].keys()

        for node in nodes:
            modules = response["nodes"][node]["modules"]
            for module in modules:
                module_properties = {
                    "name": module.get("name"),
                    "version": module.get("version"),
                    "description": module.get("description")
                }
                json_node = self.ptjsonlib.create_node_object("swModule", properties=module_properties)
                self.ptjsonlib.add_node(json_node)
                ptprint(f"Found module: {module_properties['name']} {module_properties['version']}",
                        "VULN", not self.args.json, indent=4)

        return True


    def _get_plugins(self) -> bool:
        """
        This method enumerates the plugins installed on each Elasticsearch node by sending a GET request to
        http://<host>/_cat/plugins/ and going through the JSON response

        If successful, it adds the plugin node, name and version into the JSON output

        :return: False if we get an HTTP response other than 200 OK. True if we get an HTTP 200 OK
        """
        request = self.helpers.KbnUrlParser(self.args.url, "_cat/plugins", "GET", self.kbn)
        response = self.http_client.send_request(request.url, method=request.method, headers=self.args.headers, allow_redirects=False)

        try:
            json_status = response.json().get("status", 200)
        except ValueError:
            json_status = 200

        if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK:
            ptprint(f"Could not enumerate plugins.", "OK",
                    not self.args.json, indent=4)
            ptprint(f"Received response code: {response.status_code}", "ADDITIONS", self.args.verbose, indent=4,
                    colortext=True)
            return False

        plugins = [line.split(" ") for line in response.text.split("\n")]
        del plugins[-1]    # remove empty string from plugin list

        for plugin in plugins:
            plugin = list(filter(None, plugin)) # remove empty string from plugin
            plugin_properties = {
                "esNode": plugin[0],
                "name": plugin[1],
                "version": plugin[2]
            }
            json_node = self.ptjsonlib.create_node_object("swPlugin", properties=plugin_properties)
            self.ptjsonlib.add_node(json_node)
            ptprint(f"Found plugin: {plugin_properties['name']} {plugin_properties['version']} "
                    f"on node: {plugin_properties['esNode']}", "VULN", not self.args.json, indent=4)

        return True


    def run(self) -> None:
        """
        This method executes the software enumeration.

        Runs ES version enumeration, module enumeration and plugin enumeration. If any of these 3 are successful (they
        return True) it adds the PTV-WEV-MISC-TECH vulnerability to the JSON output
        """

        es_version, modules, plugins = False, False, False

        try:
            es_version = self._get_es_version()
        except Exception as e:
            ptprint(f"Error when enumerating es version", "ERROR",
                    not self.args.json, indent=4)
            ptprint(f"{e}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

        try:
            modules = self._get_modules()
        except Exception as e:
            ptprint(f"Error when enumerating modules", "ERROR",
                    not self.args.json, indent=4)
            ptprint(f"{e}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

        try:
            plugins = self._get_plugins()
        except Exception as e:
            ptprint(f"Error when enumerating plugins", "ERROR",
                    not self.args.json, indent=4)
            ptprint(f"{e}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

        if plugins or modules or es_version:
            self.ptjsonlib.add_vulnerability("PTV-WEB-MISC-TECH")


def run(args, ptjsonlib, helpers, http_client, base_response, kbn=False):
    """Entry point for running the software test"""
    SwTest(args, ptjsonlib, helpers, http_client, base_response, kbn).run()
