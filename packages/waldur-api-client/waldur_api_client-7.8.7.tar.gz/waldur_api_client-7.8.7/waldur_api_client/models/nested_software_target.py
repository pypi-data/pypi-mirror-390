from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NestedSoftwareTarget")


@_attrs_define
class NestedSoftwareTarget:
    """
    Attributes:
        uuid (UUID):
        cpu_family (str):
        cpu_microarchitecture (str):
        path (str):
    """

    uuid: UUID
    cpu_family: str
    cpu_microarchitecture: str
    path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        cpu_family = self.cpu_family

        cpu_microarchitecture = self.cpu_microarchitecture

        path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "cpu_family": cpu_family,
                "cpu_microarchitecture": cpu_microarchitecture,
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        cpu_family = d.pop("cpu_family")

        cpu_microarchitecture = d.pop("cpu_microarchitecture")

        path = d.pop("path")

        nested_software_target = cls(
            uuid=uuid,
            cpu_family=cpu_family,
            cpu_microarchitecture=cpu_microarchitecture,
            path=path,
        )

        nested_software_target.additional_properties = d
        return nested_software_target

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
