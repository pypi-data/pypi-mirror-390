import unittest
from collections.abc import Mapping
from unittest.mock import MagicMock

from unistrant.sams import SamsClient


class SamsClientTestCase(unittest.TestCase):
    def test_get_service_map_1(self) -> None:
        content = b'<?xml version="1.0" encoding="UTF-8"?><services></services>'
        protocol = MagicMock()
        protocol.get = MagicMock(return_value=content)
        client = SamsClient("https://sams.example.org:6143/sgas", protocol)
        service_map = client.fetch_service_map()
        expected: Mapping[str, str] = {}
        self.assertDictEqual(service_map, expected)

    def test_get_service_map_2(self) -> None:
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b"<services>"
            b"<service>"
            b"<name>Registration</name>"
            b"<href>https://sams.example.org:6143/sgas/ur</href>"
            b"</service>"
            b"<service>"
            b"<name>StorageRegistration</name>"
            b"</service>"
            b"</services>"
        )
        protocol = MagicMock()
        protocol.get = MagicMock(return_value=content)
        client = SamsClient("https://sams.example.org:6143/sgas", protocol)
        service_map = client.fetch_service_map()
        expected = {
            "Registration": "https://sams.example.org:6143/sgas/ur",
        }
        self.assertDictEqual(service_map, expected)

    def test_get_service_map_3(self) -> None:
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b"<services>"
            b"<service>"
            b"<name>Registration</name>"
            b"<href>https://sams.example.org:6143/sgas/ur</href>"
            b"</service>"
            b"<service>"
            b"<href>https://sams.example.org:6143/sgas/sr</href>"
            b"</service>"
            b"</services>"
        )
        protocol = MagicMock()
        protocol.get = MagicMock(return_value=content)
        client = SamsClient("https://sams.example.org:6143/sgas", protocol)
        service_map = client.fetch_service_map()
        expected = {
            "Registration": "https://sams.example.org:6143/sgas/ur",
        }
        self.assertDictEqual(service_map, expected)

    def test_get_service_map_4(self) -> None:
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b"<services>"
            b"<service>"
            b"<name>Registration</name>"
            b"<href>https://sams.example.org:6143/sgas/ur</href>"
            b"</service>"
            b"<service>"
            b"<name>StorageRegistration</name>"
            b"<href>https://sams.example.org:6143/sgas/sr</href>"
            b"</service>"
            b"</services>"
        )
        protocol = MagicMock()
        protocol.get = MagicMock(return_value=content)
        client = SamsClient("https://sams.example.org:6143/sgas", protocol)
        service_map = client.fetch_service_map()
        expected = {
            "Registration": "https://sams.example.org:6143/sgas/ur",
            "StorageRegistration": "https://sams.example.org:6143/sgas/sr",
        }
        self.assertDictEqual(service_map, expected)
