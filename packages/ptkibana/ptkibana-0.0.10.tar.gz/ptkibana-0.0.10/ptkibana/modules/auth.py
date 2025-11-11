"""
Kibana authentication test

This module tests if a Kibana instance has authentication enabled or not
"""
from http import HTTPStatus
import requests
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Kibana authentication test"


class AuthTest:
    """
    This class tests to see if the host has Kibana has authentication enabled
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def run(self) -> None:
        """
        Executes the Kibana authentication test

        The test sends an HTTP GET request to the /app/home, /app/kibana and /api/status endpoints and if we get an HTTP response of 200 OK, the Kibana instance has authentication disabled.
        If we get a 401 UNAUTHORIZED or a redirect to the /login endpoint, the Kibana instance has authentication enabled.

        The method prints if authentication is enabled/disabled and adds a vulnerability to the JSON output if disabled
        """
        if (self.args.user and self.args.password) or self.args.api_key:
            ptprint(f"The host has authentication enabled", "OK", not self.args.json, indent=4)
            return

        for endpoint in ["app/home", "app/kibana", "api/status"]:
            ptprint(f"Accessing {self.args.url}{endpoint}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

            try:
                response = self.http_client.send_request(url=self.args.url+endpoint, method="GET", headers=self.args.headers, allow_redirects=False)
            except requests.exceptions.RequestException as error_msg:
                self.ptjsonlib.end_error(f"Error retrieving response", details=error_msg, condition=self.args.json)

            ptprint(f"Received response code {response.status_code}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

            if 300 <= response.status_code < 400 and "login" not in response.headers.get("location", "unknown"):
                try:
                    response = self.http_client.send_request(url=self.args.url + endpoint, method="GET",
                                                             headers=self.args.headers, allow_redirects=True)
                except requests.exceptions.RequestException as error_msg:
                    self.ptjsonlib.end_error(f"Error retrieving response", details=error_msg, condition=self.args.json)

            if response.status_code == HTTPStatus.UNAUTHORIZED or "/login" in response.headers.get("location", "unknown"):
                ptprint(f"The host has authentication enabled for the {endpoint} endpoint", "OK", self.args.verbose, indent=4)
                continue

            if response.status_code == HTTPStatus.OK:
                ptprint(f"The host has authentication disabled for the {endpoint} endpoint", "VULN", not self.args.json, indent=4)
                self.ptjsonlib.add_vulnerability("PTV-WEB-ELASTIC-AUTH")
                self.ptjsonlib.add_properties({"authentication": "disabled"})
                return

            ptprint(f"Could not reach {endpoint}. Received status code: {response.status_code}", "ADDITIONS",
                    self.args.verbose, indent=4)

        ptprint(f"The host has authentication enabled", "OK",
                not self.args.json, indent=4)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the authentication test"""
    AuthTest(args, ptjsonlib, helpers, http_client, base_response).run()
