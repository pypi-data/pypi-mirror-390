import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nested_software_version import NestedSoftwareVersion


T = TypeVar("T", bound="SoftwarePackage")


@_attrs_define
class SoftwarePackage:
    """
    Attributes:
        url (str):
        uuid (UUID):
        created (datetime.datetime):
        modified (datetime.datetime):
        catalog (str):
        name (str):
        catalog_name (str):
        catalog_version (str):
        version_count (int):
        versions (list['NestedSoftwareVersion']):
        description (Union[Unset, str]):
        homepage (Union[Unset, str]):
    """

    url: str
    uuid: UUID
    created: datetime.datetime
    modified: datetime.datetime
    catalog: str
    name: str
    catalog_name: str
    catalog_version: str
    version_count: int
    versions: list["NestedSoftwareVersion"]
    description: Union[Unset, str] = UNSET
    homepage: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        catalog = self.catalog

        name = self.name

        catalog_name = self.catalog_name

        catalog_version = self.catalog_version

        version_count = self.version_count

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        description = self.description

        homepage = self.homepage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "created": created,
                "modified": modified,
                "catalog": catalog,
                "name": name,
                "catalog_name": catalog_name,
                "catalog_version": catalog_version,
                "version_count": version_count,
                "versions": versions,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if homepage is not UNSET:
            field_dict["homepage"] = homepage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nested_software_version import NestedSoftwareVersion

        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        catalog = d.pop("catalog")

        name = d.pop("name")

        catalog_name = d.pop("catalog_name")

        catalog_version = d.pop("catalog_version")

        version_count = d.pop("version_count")

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = NestedSoftwareVersion.from_dict(versions_item_data)

            versions.append(versions_item)

        description = d.pop("description", UNSET)

        homepage = d.pop("homepage", UNSET)

        software_package = cls(
            url=url,
            uuid=uuid,
            created=created,
            modified=modified,
            catalog=catalog,
            name=name,
            catalog_name=catalog_name,
            catalog_version=catalog_version,
            version_count=version_count,
            versions=versions,
            description=description,
            homepage=homepage,
        )

        software_package.additional_properties = d
        return software_package

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
