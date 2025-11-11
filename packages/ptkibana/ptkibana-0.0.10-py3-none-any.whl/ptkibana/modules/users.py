"""
Kibana user enumeration module

This module enumerates available Kibana users through the /internal/security/users endpoint

Contains:
- UserEnum to perform the availability test
- run() function as an entry point for running the test
"""

from requests import Response
from http import HTTPStatus
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Kibana user enumeration"


class UserEnum:
    """
    This class enumerates available Kibana users
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _valid_response(self, response: Response, endpoint: str) -> bool:
        try:
            json_response = response.json()
        except ValueError as e:
            ptprint(f"Could not get JSON from response: {e}", "OK", not self.args.json, indent=4)
            ptprint(f"Got response: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return False

        if response.status_code != HTTPStatus.OK or (type(json_response) != list and json_response.get("status", 200) != HTTPStatus.OK):
            ptprint(f"Could not fetch {endpoint}", "OK", not self.args.json, indent=4)
            ptprint(f"Details: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return False

        return True


    def _check_privileges(self, role: str, role_privileges: list, user_properties: dict):
        """
        This method enumerates all privileges assigned to a specific role by going through the JSON output provided by the /_security/roles endpoint.

        Adds the privileges to the JSON output
        """

        for available in role_privileges:
            if available.get("name", "") == role:
                indices = available.get('indices', "")

                for index in indices:
                    privileges = index["privileges"]
                    if index["names"][0] == '*':
                        index_name = "ALL"
                    else:
                        index_name = ', '.join(index['names'])

                    user_properties["roles"][role].append({index_name: privileges})

                    ptprint(f"Privileges on indices: {index_name}: {', '.join(privileges).upper()}; Can edit restricted indices: "
                        f"{index["allow_restricted_indices"]}","VULN", not self.args.json, indent=12)


    def _print_user(self, user_properties: dict, check_roles: bool, role_privileges: list) -> None:
        """
        This method prints the user information to the terminal. If the user has a role of 'superuser', we print it in red

        If we're able to list roles from the /api/security/role endpoint, we enumerate privileges assigned to the roles of a user
        with the _check_privileges method
        """
        ptprint(f"Found user: {user_properties['username']}", "VULN", not self.args.json, indent=4)
        ptprint(f"Email: {user_properties['email']}", "VULN", not self.args.json, indent=8)

        roles = user_properties['roles']

        for role in roles:
            if role == "superuser":
                ptprint(f"\033[0mRole: \033[31m{role}", "VULN", not self.args.json, indent=8, colortext=True)
            else:
                ptprint(f"Role: {role}", "VULN", not self.args.json, indent=8)
            if check_roles:
                self._check_privileges(role, role_privileges, user_properties)
            else:
                ptprint(f"Could not enumerate privileges","OK", not self.args.json, indent=4)


    def run(self) -> None:
        """
        This method executes the Kibana user enumeration

        If users were enumerated by the ptelastic/users module (users in JSON output), the method only tries to reach the /internal/security/users endpoint.

        Send an HTTP GET request to the /internal/security/users endpoint. If the response is not HTTP 200 OK, the methods exits.
        Otherwise, the method also tries to enumerate available roles with the /api/security/role endpoint.
        The outputs are then parsed with the print_user() method from ptelastic.modules.users.Users() class
        """
        done_by_ptelastic = False

        if self.helpers.check_node("user"):
            done_by_ptelastic = True

        check_roles = False
        response = self.http_client.send_request(url=self.args.url+"internal/security/users", method="GET", headers=self.args.headers, allow_redirects=False)

        if not self._valid_response(response, "users"):
            if done_by_ptelastic:
                ptprint("The user enumeration was done by ptelastic/users module. The Kibana user enumeration failed",
                        "OK", not self.args.json, indent=4)
            return

        if done_by_ptelastic:
            ptprint("The user enumeration was done by ptelastic/users module, but the Kibana user enumeration was also successful",
                    "VULN", not self.args.json, indent=4)
            return

        try:
            users = response.json()
        except ValueError as e:
            ptprint("Could not get JSON from response.", "OK", not self.args.json, indent=4)
            ptprint(f"Got response: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return

        response = self.http_client.send_request(self.args.url+"api/security/role", method="GET",
                                                 headers=self.args.headers, allow_redirects=False)

        if self._valid_response(response, "roles"):
           check_roles = True

        for entry in users:
            user = entry.get("username", "")
            roles = entry.get("roles", [])
            user_properties = {"username": user, "email": entry["email"], "roles": roles}
            json_node = self.ptjsonlib.create_node_object("user", properties=user_properties)
            self.ptjsonlib.add_node(json_node)
            self._print_user(user_properties, check_roles, response.json())


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the UserEnum test"""
    UserEnum(args, ptjsonlib, helpers, http_client, base_response).run()
