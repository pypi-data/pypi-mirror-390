from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedSoftwareCatalogRequest")


@_attrs_define
class PatchedSoftwareCatalogRequest:
    """
    Attributes:
        name (Union[Unset, str]): Catalog name (e.g., EESSI)
        version (Union[Unset, str]): Catalog version (e.g., 2023.06)
        source_url (Union[Unset, str]): Catalog source URL
        description (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    source_url: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        version = self.version

        source_url = self.source_url

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        source_url = d.pop("source_url", UNSET)

        description = d.pop("description", UNSET)

        patched_software_catalog_request = cls(
            name=name,
            version=version,
            source_url=source_url,
            description=description,
        )

        patched_software_catalog_request.additional_properties = d
        return patched_software_catalog_request

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
