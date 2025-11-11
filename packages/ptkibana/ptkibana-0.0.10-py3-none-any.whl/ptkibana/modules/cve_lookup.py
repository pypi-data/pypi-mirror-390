"""
Kibana CVE lookup tool

This module send a request to the NVD CVE database and lists all the CVEs the Kibana version running on the host
might be vulnerable to

Contains:
- Vuln class for performing the test
- run() function as an entry point for running the test
"""
from http import HTTPStatus
import requests
from ptlibs.ptprinthelper import ptprint
from json import dumps

__TESTLABEL__ = "Kibana CVE lookup"


class Vuln:
    """
    This class prints all CVEs that the host might be vulnerable to and adds them to the JSON output
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.helpers.print_header(__TESTLABEL__)


    def _get_cvss_score(self, cve_data: dict) -> str:
        """
        This method extracts the CVSS score from the JSON output provided by the NVD API
        """
        versions = ["31", "30", "2"]

        for version in versions:
            if cvss_data := cve_data.get("cve", {}).get("metrics", {}).get(f"cvssMetricV{version}", []):
                for cvss_metric in cvss_data:
                    if "nvd" in cvss_metric.get("source", ""):
                        return cvss_metric.get("cvssData", {}).get("baseScore", "?")

        return "?"


    def _print_cve(self, cve_list: list):
        """
        This method goes through the provided list of CVEs and prints them out to the terminal and also adds them to the JSON
        output
        """
        for cve in cve_list:
            cve_id = cve["cve"]["id"]
            cvss_score = self._get_cvss_score(cve)
            msg = f"The host may be vulnerable to {cve_id}"
            link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            cvss = f"CVSS Score: {cvss_score}"
            ptprint(f"{msg:<50}{link:<52}{cvss}","VULN", not self.args.json, indent=8)

            kbn_node_key = self.helpers.check_node("swKibana")
            if kbn_node_key:
                self.ptjsonlib.add_vulnerability(f"PTV-{cve_id}", node_key=kbn_node_key)
            else:
                self.ptjsonlib.add_vulnerability(f"PTV-{cve_id}")


    def _get_kbn_version(self) -> str:
        try:
            response = self.http_client.send_request(url=self.args.url+"api/status", method="GET", headers=self.args.headers, allow_redirects=False)
        except requests.exceptions.RequestException as error_msg:
            self.ptjsonlib.end_error(f"Error retrieving response", details=error_msg, condition=self.args.json)

        if response.status_code != HTTPStatus.OK:
            ptprint("Could not reach /api/status endpoint", "OK", not self.args.json, indent=4)
            try:
                ptprint(f"Received response:\n{dumps(response.json(), indent=4)}", "ADDITIONS",
                    self.args.verbose, indent=4, colortext=True)
            except ValueError:
                ptprint(f"Received response:\n{response.text}", "ADDITIONS",
                        self.args.verbose, indent=4, colortext=True)
            return ""

        try:
            data = response.json()
        except ValueError as error_msg:
            ptprint(f"Error communicating with API: {error_msg}", "ERROR", not self.args.json, indent=4)
            return ""

        version = data.get("version", {})

        if type(version) == dict:
            version = version.get("number", "")

        return version

    def run(self) -> None:
        """
        Executes the Kibana CVE lookup

        The test first sends a request to the NVD CVE API (https://nvd.nist.gov/developers/vulnerabilities) to look for vulnerabilities in the host's Kibana version.
        It then goes through the response and prints the vulnerabilities with the _print_cve() method

        If we get a different HTTP response other than 200 OK, the test exits
        """
        kbn_version = self._get_kbn_version()

        if not kbn_version:
            ptprint(f"Could not get Kibana version", "OK", not self.args.json, indent=4)
            return

        nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:a:elastic:Kibana:{kbn_version}&isVulnerable"

        try:
            response = self.http_client.send_request(method="GET", url=nvd_url)
        except requests.exceptions.RequestException as e:
            ptprint(f"Error retrieving response from NVD database", "ERROR", not self.args.json, indent=4)
            return

        if response.status_code != HTTPStatus.OK:
            ptprint(f"Error retrieving response from NVD database. Received response: {response.status_code} {response.text}",
                    "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return

        try:
            response = response.json()
        except ValueError as e:
            ptprint(f"Could not get JSON from response: {e}", "OK", not self.args.json, indent=4)
            ptprint(f"Got response: {response.text}", "ADDITIONS", not self.args.json, indent=4, colortext=True)
            return

        cve_list = response.get("vulnerabilities", [])

        if cve_list:
            ptprint(f"Identified {response['totalResults']} possible vulnerabilities in Kibana {kbn_version}", "VULN",
                    not self.args.json, indent=4)
            self._print_cve(cve_list)
        else:
            ptprint(f"Could not identify any publicly known vulnerabilities in Kibana {kbn_version}",
                    "OK",
                    not self.args.json, indent=4)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the Vuln test"""
    Vuln(args, ptjsonlib, helpers, http_client, base_response).run()
