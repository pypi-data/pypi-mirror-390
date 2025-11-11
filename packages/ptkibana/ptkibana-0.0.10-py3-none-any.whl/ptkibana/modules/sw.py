"""
Kibana software enumeration module

This module enumerates software running on a Kibana instance
"""

from http import HTTPStatus
import requests.exceptions
from ptlibs.ptprinthelper import ptprint
from json import dumps

__TESTLABEL__ = "Kibana software enumeration"


class SwTest:
    """
    This class enumerates software running on a Kibana host
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _add_to_json(self, properties: dict, node_name) -> None:
        """
        This method adds a JSON node to the JSON output with the specified properties and node_name
        """
        json_node = self.ptjsonlib.create_node_object(node_name, properties=properties)
        self.ptjsonlib.add_node(json_node)


    def _list_plugins(self, data: dict) -> None:
        """
        This method retrieves available plugins and their status, prints them out and adds them to the JSON output
        """
        status_object = data.get("status", {})
        plugins = status_object.get("statuses", status_object.get("plugins", {}))

        if plugins and type(plugins) == list:
            id_key = "name" if plugins[0].get("name", "") else "id"
            ptprint(f"Found plugins:", "INFO", not self.args.json, indent=4)
            for plugin in plugins:
                status = plugin.get('state', 'unknown')
                name = plugin.get(id_key, "").replace("plugin:", "")
                if "core:" in name:
                    continue
                self._add_to_json({"name": name, "status": status}, "swPlugin")
                ptprint(f"Name: {name:<35} Status: {status:<15}", "INFO", not self.args.json, indent=8)

        elif plugins and type(plugins) == dict:
            ptprint(f"Found plugins:", "INFO", not self.args.json, indent=4)
            for plugin in plugins.keys():
                status = plugins.get(plugin, {}).get("level", "unknown")
                self._add_to_json({"name": plugin, "status": status}, "swPlugin")
                ptprint(f"Name: {plugin:<35} Status: {status:<15}", "INFO", not self.args.json, indent=8)

        else:
            ptprint(f"Could not retrieve available plugins", "OK", not self.args.json, indent=4)


    def _list_core_plugins(self, data: dict) -> None:
        """
        This method retrieves available core plugins and their status, prints them out and adds them to the JSON output
        """
        if cores := data.get("status", {}).get("core", {}):
            for core in cores:
                name = core
                status = cores.get(core, {}).get("level", "unknown")
                self._add_to_json({"id": name, "status": status}, "swCorePlugin")
                ptprint(f"Name: {name:<35} Status: {status:<15}", "INFO",
                        not self.args.json, indent=8)
            return

        id_key = "name" if data.get("status", {}).get("statuses", [{}])[0].get("name", "") else "id"
        cores = [core for core in data.get("status", {}).get("statuses", {}) if "core" in core.get(id_key, "")]

        if cores:
            ptprint(f"Found core plugins:", "INFO", not self.args.json, indent=4)
            for core in cores:
                name = core.get(id_key, "").replace("core:", "")
                status = core.get('state', 'unknown')
                self._add_to_json({"id": name, "status": status}, "swCorePlugin")
                ptprint(f"Name: {name:<35} Status: {status:<15}", "INFO",
                        not self.args.json, indent=8)

        else:
            ptprint(f"Could not retrieve available core plugins", "OK", not self.args.json, indent=4)


    def _list_os_properties(self, data: dict) -> None:
        """
        This method retrieves OS properties, prints them out and adds them to the JSON output
        """
        os_properties = data.get("metrics", {}).get("os", {})

        platform = os_properties.get('platform', '')
        platform_release = os_properties.get('platformRelease', '')
        distro = os_properties.get('distro', '')
        distro_release = os_properties.get('distroRelease', '')

        if not any([platform, platform_release, distro_release, distro]):
            ptprint(f"Could not retrieve OS properties", "OK", not self.args.json, indent=4)
            return

        ptprint(f"OS properties:", "INFO", not self.args.json, indent=4)
        ptprint(f"{'Platform:':<41} {platform}", "INFO",
                not self.args.json, indent=8) if platform else None
        ptprint(f"{'Release:':<41} {platform_release}", "INFO",
                not self.args.json, indent=8) if platform_release else None
        ptprint(f"{'Distro:':<41} {distro}", "INFO",
                not self.args.json, indent=8) if distro else None
        ptprint(f"{'Distro release:':<41} {distro_release}", "INFO",
                not self.args.json, indent=8) if distro_release else None

        self._add_to_json({
                "platform": os_properties.get('platform', ''),
                "release": os_properties.get('platformRelease', ''),
                "distro": os_properties.get('distro', ''),
                "distroRelease": os_properties.get('distroRelease', '')
             },
        "osProperties")


    def _list_kbn_version(self, data: dict) -> None:
        """
        This method retrieves the Kibana version, prints it out and adds it to the JSON output
        """
        version = data.get("version", {})

        if type(version) == dict:
            version = version.get("number", "")

        if version:
            self._add_to_json({"name": data.get("name", ""), "version": version}, "swKibana")
            ptprint(f"{'Kibana version:':<45} {version}", "INFO", not self.args.json, indent=4)
        else:
            ptprint("Could not enumerate version", "OK", not self.args.json, indent=4)


    def run(self) -> None:
        """
        Executes the Kibana software enumeration module

        This method first retrieves available plugins, core plugins, os properties and the Kibana instance version.
        It does so by sending an HTTP GET request to the /api/status output and then going through the JSON response.

        If successful, it prints the information out and adds it to the JSON output.
        """
        try:
            response = self.http_client.send_request(url=self.args.url+"api/status", method="GET", headers=self.args.headers, allow_redirects=False)
        except requests.exceptions.RequestException as error_msg:
            self.ptjsonlib.end_error(f"Error retrieving response", details=error_msg, condition=self.args.json)

        if response.status_code != HTTPStatus.OK:
            ptprint("Could not reach /api/status endpoint", "OK", not self.args.json, indent=4)
            try:
                ptprint(f"Received response:\n{response.text}", "ADDITIONS",
                    self.args.verbose, indent=4, colortext=True)
            except ValueError:
                ptprint(f"Received response:\n{response.text}", "ADDITIONS",
                        self.args.verbose, indent=4, colortext=True)
            return

        try:
            data = response.json()
        except ValueError as error_msg:
            ptprint(f"Error communicating with API: {error_msg}", "ERROR", not self.args.json, indent=4)
            return

        self._list_kbn_version(data)
        self._list_core_plugins(data)
        self._list_plugins(data)
        self._list_os_properties(data)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the SW enumeration module"""
    SwTest(args, ptjsonlib, helpers, http_client, base_response).run()
