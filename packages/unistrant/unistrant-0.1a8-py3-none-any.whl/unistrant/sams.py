import xml.etree.ElementTree as ET
from collections.abc import Mapping

from unistrant.http import HttpProtocol
from unistrant.record import RecordDocument, RecordType


def service_for_record(record_type: RecordType) -> str:
    match record_type:
        case RecordType.Compute:
            return "Registration"
        case RecordType.Storage:
            return "StorageRegistration"
        case RecordType.Cloud:
            return "CloudRegistration"
        case RecordType.SoftwareAccounting:
            return "SoftwareAccountingRegistration"


class SamsClient:
    def __init__(self, url: str, protocol: HttpProtocol) -> None:
        self.url = url
        self.protocol = protocol
        self._service_map: Mapping[str, str] = {}

    @property
    def service_map(self) -> Mapping[str, str]:
        if not self._service_map:
            self._service_map = self.fetch_service_map()
        return self._service_map

    def fetch_service_map(self) -> Mapping[str, str]:
        content = self.protocol.get(self.url)

        service_map = {}
        tree = ET.fromstring(content)
        for service in tree.findall("service"):
            if (element := service.find("name")) is not None:
                name = element.text
            else:
                continue
            if (element := service.find("href")) is not None:
                href = element.text
            else:
                continue
            if name and href:
                service_map[name] = href
        return service_map

    def upload_record_document(self, document: RecordDocument) -> None:
        service_name = service_for_record(document.record_type)
        self.protocol.post(self.service_map[service_name], document.bytes)
