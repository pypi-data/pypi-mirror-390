from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SoftwarePackageRequest")


@_attrs_define
class SoftwarePackageRequest:
    """
    Attributes:
        catalog (str):
        name (str):
        description (Union[Unset, str]):
        homepage (Union[Unset, str]):
    """

    catalog: str
    name: str
    description: Union[Unset, str] = UNSET
    homepage: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        catalog = self.catalog

        name = self.name

        description = self.description

        homepage = self.homepage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "catalog": catalog,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if homepage is not UNSET:
            field_dict["homepage"] = homepage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        catalog = d.pop("catalog")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        homepage = d.pop("homepage", UNSET)

        software_package_request = cls(
            catalog=catalog,
            name=name,
            description=description,
            homepage=homepage,
        )

        software_package_request.additional_properties = d
        return software_package_request

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
