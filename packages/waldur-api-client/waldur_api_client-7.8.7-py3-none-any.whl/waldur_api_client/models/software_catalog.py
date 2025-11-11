import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SoftwareCatalog")


@_attrs_define
class SoftwareCatalog:
    """
    Attributes:
        url (str):
        uuid (UUID):
        created (datetime.datetime):
        modified (datetime.datetime):
        name (str): Catalog name (e.g., EESSI)
        version (str): Catalog version (e.g., 2023.06)
        package_count (int):
        source_url (Union[Unset, str]): Catalog source URL
        description (Union[Unset, str]):
    """

    url: str
    uuid: UUID
    created: datetime.datetime
    modified: datetime.datetime
    name: str
    version: str
    package_count: int
    source_url: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        name = self.name

        version = self.version

        package_count = self.package_count

        source_url = self.source_url

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "created": created,
                "modified": modified,
                "name": name,
                "version": version,
                "package_count": package_count,
            }
        )
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        name = d.pop("name")

        version = d.pop("version")

        package_count = d.pop("package_count")

        source_url = d.pop("source_url", UNSET)

        description = d.pop("description", UNSET)

        software_catalog = cls(
            url=url,
            uuid=uuid,
            created=created,
            modified=modified,
            name=name,
            version=version,
            package_count=package_count,
            source_url=source_url,
            description=description,
        )

        software_catalog.additional_properties = d
        return software_catalog

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
