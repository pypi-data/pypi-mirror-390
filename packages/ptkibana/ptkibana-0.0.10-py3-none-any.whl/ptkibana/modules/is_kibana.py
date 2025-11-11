"""
Kibana availability test

This module implements a test that checks if the provided host is running Kibana or not

Contains:
- IsKibana to perform the availability test
- run() function as an entry point for running the test
"""
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Kibana availability test"


class IsKibana:
    """
    This class checks to see if a host is running Kibana by looking for the 'kbn' or 'kibana' string in the servers response
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _check_headers(self, headers: object, value: str) -> bool:
        """
        :return: True if the response headers contain the provided value.
        """
        for current in headers:
            if value in current.lower():
                return True

        return False

    def run(self) -> None:
        """
        Executes the Kibana availability test

        The method looks for the 'kibana' and 'kbn' strings in the response body and headers

        If the response body/headers contain the string '̈́kibana' the method prints a message that the host is running Kibana.
        If the response body/headers contain the string 'kbn' the method prints a message that the host might be running Kibana.

        Otherwise, exits with an error
        """

        response = self.base_response

        certain = ["kibana" in response.text.lower(), self._check_headers(response.headers.values(), "kibana")]
        probable = ["kbn" in response.text.lower(), self._check_headers(response.headers.keys(), "kbn")]

        if any(certain) :
            ptprint("The host is running Kibana", "INFO", not self.args.json, indent=4)
        elif any(probable):
            ptprint("The host might be running Kibana", "INFO", not self.args.json, indent=4)
        else:
            self.ptjsonlib.end_error("The host is not running kibana", self.args.json)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the IsKibana test"""
    IsKibana(args, ptjsonlib, helpers, http_client, base_response).run()
