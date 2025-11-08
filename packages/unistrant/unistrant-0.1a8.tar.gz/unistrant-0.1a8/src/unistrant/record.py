import enum
import xml.etree.ElementTree as ET
from collections.abc import Collection
from pathlib import Path

from unistrant.error import RecordError


class RecordType(enum.StrEnum):
    Compute = "Compute"
    Storage = "Storage"
    Cloud = "Cloud"
    SoftwareAccounting = "SoftwareAccounting"


class RecordTag(enum.StrEnum):
    JobUsageRecord = "{http://schema.ogf.org/urf/2003/09/urf}JobUsageRecord"
    StorageUsageRecord = "{http://eu-emi.eu/namespaces/2011/02/storagerecord}StorageUsageRecord"
    CloudComputeRecord = "{http://sams.snic.se/namespaces/2016/04/cloudrecords}CloudComputeRecord"
    CloudStorageRecord = "{http://sams.snic.se/namespaces/2016/04/cloudrecords}CloudStorageRecord"
    SoftwareAccountingRecord = "{http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords}SoftwareAccountingRecord"


class RecordCollectionTag(enum.StrEnum):
    UsageRecords = "{http://schema.ogf.org/urf/2003/09/urf}UsageRecords"
    StorageUsageRecords = "{http://eu-emi.eu/namespaces/2011/02/storagerecord}StorageUsageRecords"
    CloudRecords = "{http://sams.snic.se/namespaces/2016/04/cloudrecords}CloudRecords"
    SoftwareAccountingRecords = "{http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords}SoftwareAccountingRecords"


class Record:
    def __init__(self, element: ET.Element):
        self.element = element

        try:
            self.tag = RecordTag(element.tag)
        except ValueError:
            raise RecordError(f"Unsupported tag {element.tag}")

    @property
    def record_type(self) -> RecordType:
        match self.tag:
            case RecordTag.JobUsageRecord:
                return RecordType.Compute
            case RecordTag.StorageUsageRecord:
                return RecordType.Storage
            case RecordTag.CloudComputeRecord | RecordTag.CloudStorageRecord:
                return RecordType.Cloud
            case RecordTag.SoftwareAccountingRecord:
                return RecordType.SoftwareAccounting


class RecordFile:
    def __init__(self, path: Path):
        with path.open("rb") as f:
            try:
                tree = ET.parse(f)
            except ET.ParseError as e:
                raise RecordError(f"Error parsing file {path.name}: {str(e)}")
        ET.indent(tree)
        self.path = path
        self.tree = tree

        self.tag: RecordTag | RecordCollectionTag
        root = self.tree.getroot()
        tag = root.tag
        try:
            self.tag = RecordTag(tag)
        except ValueError:
            try:
                self.tag = RecordCollectionTag(tag)
            except ValueError:
                raise RecordError(f"Root element has unsupported tag {tag}")
        match self.tag:
            case RecordCollectionTag():
                for sub_element in root:
                    try:
                        RecordTag(sub_element.tag)
                    except ValueError:
                        raise RecordError(f"Element has unsupported tag {sub_element.tag}")

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def records(self) -> Collection[Record]:
        match self.tag:
            case RecordTag():
                return [Record(self.tree.getroot())]

            case RecordCollectionTag.UsageRecords:
                return [Record(element) for element in self.tree.findall(RecordTag.JobUsageRecord)]

            case RecordCollectionTag.StorageUsageRecords:
                return [Record(element) for element in self.tree.findall(RecordTag.StorageUsageRecord)]

            case RecordCollectionTag.CloudRecords:
                return [
                    Record(element)
                    for element in self.tree.findall(RecordTag.CloudComputeRecord) + self.tree.findall(RecordTag.CloudStorageRecord)
                ]

            case RecordCollectionTag.SoftwareAccountingRecords:
                return [Record(element) for element in self.tree.findall(RecordTag.SoftwareAccountingRecord)]


class RecordDocument:
    def __init__(self, record_type: RecordType, records: Collection[Record]):
        self.record_type = record_type
        self.records = records
        match record_type:
            case RecordType.Compute:
                tag = RecordCollectionTag.UsageRecords
            case RecordType.Storage:
                tag = RecordCollectionTag.StorageUsageRecords
            case RecordType.Cloud:
                tag = RecordCollectionTag.CloudRecords
            case RecordType.SoftwareAccounting:
                tag = RecordCollectionTag.SoftwareAccountingRecords
        tree = ET.Element(str(tag))
        for record in records:
            tree.append(record.element)
        ET.indent(tree)
        self.tree = tree

    @property
    def xml(self) -> str:
        return ET.tostring(self.tree, encoding="unicode")

    @property
    def bytes(self) -> bytes:
        return ET.tostring(self.tree)
