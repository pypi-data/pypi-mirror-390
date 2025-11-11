"""
Kibana HTTP/S test

This module tests if a Kibana instance is running on HTTPS or HTTP
"""
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Kibana HTTP/S test"


class HttpTest:
    """
    This class tests to see if the host has Kibana running on HTTP or HTTPS
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
        Executes the Kibana HTTP/S test

        Checks to see if the URL we have sent the initial request contains http:// or https:// in the URL
        """

        if "https://" in self.args.url:
            ptprint(f"The host is running on HTTPS", "OK", not self.args.json, indent=4)
            return

        ptprint(f"The host is running on HTTP", "VULN", not self.args.json, indent=4)
        self.ptjsonlib.add_vulnerability("PTV-KIBANA-MISC-HTTP")


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the HTTP/S test"""
    HttpTest(args, ptjsonlib, helpers, http_client, base_response).run()
