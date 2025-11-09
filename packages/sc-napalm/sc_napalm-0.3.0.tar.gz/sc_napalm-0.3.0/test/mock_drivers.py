from pathlib import Path
import os
import json
from inspect import isclass
import re

from google.protobuf import json_format
import custom_napalm
from jnpr.junos.factory.optable import OpTable

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


def mock_netmiko_send(path: str, cmd: str, encoding="text") -> str:
    """
    Generic 'translate a device command to a valid filename, then read
    data from that file'
    path: Path object pointing to where that file resides
    cmd: the command string passed to the relevant netmiko/junper/etc "send_command" method
    """
    cmd = cmd.replace(" ", "_")
    cmd = cmd.replace("*", "star")

    if encoding == "json":
        cmd += ".json"
    else:
        cmd += ".txt"

    cmd_file = str(path + "/" + cmd)

    with open(cmd_file, encoding="utf-8") as fh:
        cmd_txt = fh.read()

    return cmd_txt


class MockDriver:
    def __init__(self, test_dir: Path, **kwargs):
        self.test_dir = test_dir

    def open(self):
        pass

    def close(self):
        pass


class MockNCManager:
    """
    Fake ncclient 'manager' class that overrides 'dispatch'
    to pull xml data from a file and save it to an .xml
    attribute
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def dispatch(self, element):
        # we're going to assume that the RPC call is a `get` with a `filter`
        # and that the filename in the mock data corresponds to the highest
        # element in the filter.
        filter_no_ns = re.sub(r"\{.+\}", "", element[0][0].tag)
        file_name = str(self.file_path / f"get-{filter_no_ns}.xml")

        with open(file_name) as fh:
            data = fh.read()

        self.xml = data

        return self


class MockSRLAPI(object):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def open(self):
        pass

    def close(self):
        pass

    def _gnmiGet(self, prefix, paths, pathType):
        """
        for each path in the set of paths
        look for a file named based on that path with "/"
        replaced with "_".
        Contatenate the results of those files together
        """
        output = ""
        for path in paths:
            # removing leading slashes and indexes
            path = re.sub(r"^/", "", path)
            path = re.sub(r"\[.+\]", "", path)
            path = re.sub(r"[/-]", "_", path)
            cmd_file = f"{self.file_path}/{path}.txt"
            with open(cmd_file, encoding="utf-8") as fh:
                output += fh.read()
        print(output)

        output = re.sub(r"\'", '"', output)
        return json_format.ParseFromString(output)


class MockEOS(MockDriver, custom_napalm.SCEOSDriver):
    driver_name = "eos"

    def __init__(self, test_dir, **kwargs):
        MockDriver.__init__(self, test_dir, **kwargs)
        self.transport = "ssh"

    def _run_commands(self, cmds: list[str], encoding="json"):
        """
        Mocks eos _run_commands, assumes your file is json-encoded
        and returns a data structure based on that.
        """
        result = []
        for cmd in cmds:
            cmd_text = mock_netmiko_send(str(self.test_dir), cmd, encoding=encoding)
            try:
                cmd_json = json.loads(cmd_text)
            except json.decoder.JSONDecodeError:
                cmd_json = {}

            result.append(cmd_json)

        return result


class MockIOSXR(MockDriver, custom_napalm.SCIOSXR):
    driver_name = "iosxr"

    def open(self):
        self.device = MockNCManager(self.test_dir)


class MockJunos(MockDriver, custom_napalm.SCJunOS):
    driver_name = "junos"

    def __init__(self, test_dir, **kwargs):
        """
        With junos we are going to override the pyEZ initializer for
        """
        MockDriver.__init__(self, test_dir, **kwargs)
        self.device = None

        for obj in custom_napalm.junos.junos_views.__dict__.values():
            if isclass(obj) and issubclass(obj, OpTable):
                # only override initializer if we have mock data for this view
                mock_rpc = f"{self.test_dir}/{obj.GET_RPC}.xml"
                if not os.path.isfile(mock_rpc):
                    continue

                def new_init(obj, dev=None, xml=None, path=None, use_filter=True):
                    obj._dev = None
                    obj.view = obj.VIEW
                    obj._key_list = []
                    obj._path = f"{self.test_dir}/{obj.GET_RPC}.xml"
                    # obj._lxml = etree.parse(f"{self.path}/{obj.GET_RPC}.xml")
                    # obj.xml = etree.parse(f"{self.path}/{obj.GET_RPC}.xml")
                    obj._use_filter = obj.USE_FILTER and use_filter
                    if obj._dev is not None:
                        obj._use_filter = obj._use_filter and obj._dev._use_filter

                obj.__init__ = new_init


class MockNXOS(MockDriver, custom_napalm.SCNXOS):
    driver_name = "nxos"

    def _send_command(self, cmd: str):
        return mock_netmiko_send(str(self.test_dir), cmd)


class MockNokiaSRL(MockDriver, custom_napalm.SCNokiaSRLDriver):
    driver_name = "srl"

    def __init__(self, test_dir, **kwargs):
        MockDriver.__init__(self, test_dir, **kwargs)
        self.device = MockSRLAPI(test_dir)
