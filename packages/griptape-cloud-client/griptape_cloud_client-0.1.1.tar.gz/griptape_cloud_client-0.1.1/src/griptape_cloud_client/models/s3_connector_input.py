from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="S3ConnectorInput")


@_attrs_define
class S3ConnectorInput:
    """
    Attributes:
        aws_access_key_id (str):
        aws_secret_access_key (str):
        uris (list[str]):
        encoding (Union[Unset, str]):
    """

    aws_access_key_id: str
    aws_secret_access_key: str
    uris: list[str]
    encoding: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aws_access_key_id = self.aws_access_key_id

        aws_secret_access_key = self.aws_secret_access_key

        uris = self.uris

        encoding = self.encoding

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "uris": uris,
            }
        )
        if encoding is not UNSET:
            field_dict["encoding"] = encoding

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        aws_access_key_id = d.pop("aws_access_key_id")

        aws_secret_access_key = d.pop("aws_secret_access_key")

        uris = cast(list[str], d.pop("uris"))

        encoding = d.pop("encoding", UNSET)

        s3_connector_input = cls(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            uris=uris,
            encoding=encoding,
        )

        s3_connector_input.additional_properties = d
        return s3_connector_input

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
