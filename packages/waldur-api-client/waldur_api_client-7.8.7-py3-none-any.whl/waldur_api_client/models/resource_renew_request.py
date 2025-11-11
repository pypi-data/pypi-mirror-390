from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_renew_request_limits import ResourceRenewRequestLimits


T = TypeVar("T", bound="ResourceRenewRequest")


@_attrs_define
class ResourceRenewRequest:
    """
    Attributes:
        extension_months (int): Number of months to extend the subscription by.
        limits (Union[Unset, ResourceRenewRequestLimits]): Optional new limits for the resource. Supports upgrades only.
    """

    extension_months: int
    limits: Union[Unset, "ResourceRenewRequestLimits"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        extension_months = self.extension_months

        limits: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "extension_months": extension_months,
            }
        )
        if limits is not UNSET:
            field_dict["limits"] = limits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_renew_request_limits import ResourceRenewRequestLimits

        d = dict(src_dict)
        extension_months = d.pop("extension_months")

        _limits = d.pop("limits", UNSET)
        limits: Union[Unset, ResourceRenewRequestLimits]
        if isinstance(_limits, Unset):
            limits = UNSET
        else:
            limits = ResourceRenewRequestLimits.from_dict(_limits)

        resource_renew_request = cls(
            extension_months=extension_months,
            limits=limits,
        )

        resource_renew_request.additional_properties = d
        return resource_renew_request

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
