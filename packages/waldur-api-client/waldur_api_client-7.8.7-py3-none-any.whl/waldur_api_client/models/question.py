from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.question_options import QuestionOptions


T = TypeVar("T", bound="Question")


@_attrs_define
class Question:
    """
    Attributes:
        uuid (UUID):
        question_options (list['QuestionOptions']):
        required (Union[Unset, bool]):
        description (Union[Unset, str]):
        user_guidance (Union[Unset, str]): Additional guidance text visible to users when answering and reviewing
    """

    uuid: UUID
    question_options: list["QuestionOptions"]
    required: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    user_guidance: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        question_options = []
        for question_options_item_data in self.question_options:
            question_options_item = question_options_item_data.to_dict()
            question_options.append(question_options_item)

        required = self.required

        description = self.description

        user_guidance = self.user_guidance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "question_options": question_options,
            }
        )
        if required is not UNSET:
            field_dict["required"] = required
        if description is not UNSET:
            field_dict["description"] = description
        if user_guidance is not UNSET:
            field_dict["user_guidance"] = user_guidance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.question_options import QuestionOptions

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        question_options = []
        _question_options = d.pop("question_options")
        for question_options_item_data in _question_options:
            question_options_item = QuestionOptions.from_dict(question_options_item_data)

            question_options.append(question_options_item)

        required = d.pop("required", UNSET)

        description = d.pop("description", UNSET)

        user_guidance = d.pop("user_guidance", UNSET)

        question = cls(
            uuid=uuid,
            question_options=question_options,
            required=required,
            description=description,
            user_guidance=user_guidance,
        )

        question.additional_properties = d
        return question

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
