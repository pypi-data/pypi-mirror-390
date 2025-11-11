"""
Kibana Elasticsearch proxy test

This module tests if a Kibana instance can serve as a proxy for Elasticsearch queries
"""
import importlib
import os
import sys
import threading
from http import HTTPStatus
from io import StringIO
from types import ModuleType
import requests
from ptlibs.ptprinthelper import ptprint
from ptelastic.modules.is_elastic import IsElastic
from ptelastic.helpers.helpers import Helpers

__TESTLABEL__ = "Kibana Elasticsearch proxy test"

from ptlibs.threads import ptthreads
from ptelastic.helpers._thread_local_stdout import ThreadLocalStdout
import ptelastic
from ptelastic.helpers.helpers import Helpers

class ProxyTest:
    """
    This class tests to see if the host has Kibana can serve as a proxy for Elasticsearch queries
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response
        self.helpers.print_header(__TESTLABEL__)
        self._lock = threading.Lock()
        self.ptthreads = ptthreads.PtThreads()
        self._lock = threading.Lock()
        self.thread_local_stdout = ThreadLocalStdout(sys.stdout)
        self.thread_local_stdout.activate()

    def _verify(self) -> bool:
        """
        This method verifies that the /api/console/proxy endpoint is available, and we can send ES queries

        :return: True if the proxy is available. False otherwise
        """
        headers = self.args.headers.copy()
        headers.update({"kbn-xsrf": "true"})

        try:
            self.es_base_response = self.http_client.send_request(url=self.args.url+"api/console/proxy?path=/&method=GET", method="POST",
                                                     headers=headers)
        except requests.exceptions.RequestException as error_msg:
            ptprint(f"Error communicating with /api/console/proxy.", "ERROR", not self.args.json, indent=4)
            ptprint(f"{error_msg}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return False


        if self.es_base_response.status_code != HTTPStatus.OK:
            ptprint(f"Error communicating with /api/console/proxy.", "ERROR", not self.args.json, indent=4)
            ptprint(f"Received response: {self.es_base_response.text}", "ADDITIONS", self.args.verbose, indent=4,
                    colortext=True)
            return False

        self.ptjsonlib.add_vulnerability("PTV-KIBANA-ES-PROXY")

        return True

    def _get_all_available_modules(self) -> list:
        """
        Returns a list of available Python module names from the ptelastic 'modules' directory.

        Modules must:
        - Not start with an underscore
        - Have a '.py' extension
        """
        modules_folder = os.path.join(os.path.dirname(ptelastic.__file__), "modules")
        available_modules = [
            f.rsplit(".py", 1)[0]
            for f in sorted(os.listdir(modules_folder))
            if f.endswith(".py") and not f.startswith("_")
        ]
        return available_modules


    def _import_module_from_path(self, module_name: str) -> ModuleType:
        """
        Dynamically imports a Python module from a given file path.

        This method uses `importlib` to load a module from a specific file location.
        The module is then registered in `sys.modules` under the provided name.

        Args:
            module_name (str): Name under which to register the module.

        Returns:
            ModuleType: The loaded Python module object.

        Raises:
            ImportError: If the module cannot be found or loaded.
        """
        module_path = os.path.join(os.path.dirname(ptelastic.__file__), "modules", f"{module_name}.py")

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            raise ImportError(f"Cannot find spec for {module_name} at {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


    def run_single_module(self, module_name: str) -> None:
        """
        Safely loads and executes a specified module's `run()` function.

        The method locates the module file in the "modules" directory, imports it dynamically,
        and executes its `run()` method with provided arguments and a shared `ptjsonlib` object.
        It also redirects stdout/stderr to a thread-local buffer for isolated output capture.

        If the module or its `run()` method is missing, or if an error occurs during execution,
        it logs appropriate messages to the user.

        Args:
            module_name (str): The name of the module (without `.py` extension) to execute.
        """
        try:
            with self._lock:
                module = self._import_module_from_path(module_name)

            if hasattr(module, "run") and callable(module.run):
                buffer = StringIO()
                self.thread_local_stdout.set_thread_buffer(buffer)

                self.args.headers.update({"kbn-xsrf": "true"})


                try:
                    module.run(
                        args=self.args,
                        ptjsonlib=self.ptjsonlib,
                        helpers=Helpers(args=self.args, ptjsonlib=self.ptjsonlib, http_client=self.http_client),
                        http_client=self.http_client,
                        base_response=self.es_base_response,
                        kbn=True
                    )

                except Exception as e:
                    ptprint(e, "ERROR", not self.args.json)
                    error = e
                else:
                    error = None
                finally:
                    self.thread_local_stdout.clear_thread_buffer()
                    with self._lock:
                        ptprint(buffer.getvalue(), "TEXT", not self.args.json, end="\n")
            else:
                ptprint(f"Module '{module_name}' does not have 'run' function", "WARNING", not self.args.json)

        except FileNotFoundError as e:
            ptprint(f"Module '{module_name}' not found", "ERROR", not self.args.json)
        except Exception as e:
            ptprint(f"Error running module '{module_name}': {e}", "ERROR", not self.args.json)


    def run(self) -> None:
        """
        Executes the Kibana proxy test

        First verifies that the proxy is available.

        Then loads modules specified with the -ests/--elasticsearch-tests (all if none specified) and starts them.
        """
        if not self._verify():
            return

        tests = self.args.elasticsearch_tests or self._get_all_available_modules()

        if "is_elastic" in tests:
            tests.remove("is_elastic")
            try:
                IsElastic(
                    args=self.args,
                    ptjsonlib=self.ptjsonlib,
                    helpers=self.helpers,
                    http_client=self.http_client,
                    base_response=self.es_base_response,
                    kbn=True
                ).run()
                ptprint(" ", "TEXT", not self.args.json)
            except IsElastic.NotElasticsearch as e:
                ptprint(f"{e}", "OK", not self.args.verbose, indent=4)
                ptprint(" ", "TEXT", not self.args.json)
                return

        self.ptthreads.threads(tests, self.run_single_module, self.args.threads)

def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the proxy test"""
    ProxyTest(args, ptjsonlib, helpers, http_client, base_response).run()
