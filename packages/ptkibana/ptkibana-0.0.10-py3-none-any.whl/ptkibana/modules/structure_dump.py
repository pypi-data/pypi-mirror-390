"""
Kibana data structure test

Contains:
- StrucDump to perform the data structure test
- run() function as an entry point for running the test
"""

from http import HTTPStatus
from ptlibs.ptprinthelper import ptprint
import json

__TESTLABEL__ = "Kibana data structure test"


class StrucDump:
    """
    This class gets all Elasticsearch indices from a Kibana instance and then dumps what fields each index contains
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object, kbn: bool) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.kbn = kbn

        self.helpers.print_header(__TESTLABEL__)


    def _check_json(self, index_name: str) -> bool:
        """
        This method goes through the ptjsonlib JSON object to see if an index structure was already mapped by the ptelastic/structure_dump module.

        :return: True if the index was already mapped. False otherwise
        """
        for node in self.ptjsonlib.json_object.get("results", {}).get("nodes", {}):
            if node.get("type", "") == "indexStructure" and node.get("properties", {}).get("name", "") == index_name:
                return True

        return False


    def _get_indices(self) -> list:
        """
        This method retrieves all available Elasticsearch indices from the Kibana instance

        :return: List of indices if successful. Empty list otherwise
        """
        response = self.http_client.send_request(url=self.args.url+"api/index_management/indices", method="GET", headers=self.args.headers)

        try:
            json_response = response.json()
            json_status = json_response.get("status", 200)
        except ValueError:
            ptprint("The host returned non-JSON data", "ERROR", not self.args.json, indent=4)
            return []
        except AttributeError:
            json_status = 200

        if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK:
            ptprint(f"Error fetching indices. Received response: {response.status_code}", "ERROR",
                    not self.args.json, indent=4)
            ptprint(f"Received response: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return []

        indices = [index.get("name", "unknown") for index in json_response]

        return indices


    def _get_fields(self, mapping, prefix="") -> list:
        """
        This method recursively collects all field paths from ES mapping.

        :return: List of fields in an index mapping
        """
        if not mapping:
            return []

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
        Executes the Kibana data structure test

        The method first checks if an index was already mapped by the ptelastic/structure_dump module.

        The method then gets all indices with the _get_indices() method and then prints fields in an index by sending a request to
        the /api/index_management/mapping/<index name> endpoint and then retrieving all the fields with the method _get_fields()

        If the -b/--built-in switch is provided, the method prints hidden indices (indices starting with .) along with all other indices.
        """
        printed = False

        for index in self._get_indices():
            if not self.args.built_in and index.startswith("."):
                continue

            if self._check_json(index):
                ptprint(f"The index {index} was already mapped by the ptelastic/structure_dump module", "VULN",
                        not self.args.json, indent=4)
                printed = True
                continue

            response = self.http_client.send_request(url=self.args.url+f"api/index_management/mapping/{index}", method="GET", headers=self.args.headers)

            try:
                json_status = response.json().get("status", 200)
            except ValueError:
                json_status = 200

            if response.status_code != HTTPStatus.OK or json_status != HTTPStatus.OK:
                ptprint(f"Error fetching index {index}. Received response: {response.status_code} {json.dumps(response.json(), indent=4)}",
                        "ADDITIONS",
                        self.args.verbose, indent=4, colortext=True)
                continue

            response = response.json()

            fields = self._get_fields(mapping=response.get("mappings", {}))

            if not fields:
                ptprint(f"Found index: {index}. It has no mappings", "VULN", not self.args.json, indent=4)
                mapping_node = self.ptjsonlib.create_node_object("indexStructure", properties={"mappings": None})
                self.ptjsonlib.add_node(mapping_node)
                printed = True
                continue

            mapping_node = self.ptjsonlib.create_node_object("indexStructure", properties=response.get("mappings", {}))
            self.ptjsonlib.add_node(mapping_node)

            ptprint(f"Index {index}", "VULN", not self.args.json, indent=4)
            ptprint(', '.join(fields), "VULN", not self.args.json, indent=8)
            printed = True

        if not printed:
            ptprint("Could not find any non built-in indices", "INFO", not self.args.json, indent=4)

def run(args, ptjsonlib, helpers, http_client, base_response, kbn=False):
    """Entry point for running the StrucDump test"""
    StrucDump(args, ptjsonlib, helpers, http_client, base_response, kbn).run()
