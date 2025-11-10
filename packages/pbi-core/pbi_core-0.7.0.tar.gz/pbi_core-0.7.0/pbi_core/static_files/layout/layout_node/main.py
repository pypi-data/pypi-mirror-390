import json
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from attrs import Attribute

from pbi_core.attrs import BaseValidation, fields
from pbi_core.lineage import LineageNode

from .find import FindMixin
from .xpath import XPathMixin

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel

LAYOUT_ENCODING = "utf-16-le"


T = TypeVar("T", bound="LayoutNode")


class LayoutNode(BaseValidation, XPathMixin, FindMixin):
    _name_field: str | None = None  # name of the field used to populate __repr__

    def __repr__(self) -> str:
        return json.dumps(self.serialize(), indent=2)

    @staticmethod
    def serialize_helper(value: Any) -> Any:
        """Helper function to serialize a value.

        We need to separate from the main function to handle cases where there is a list of
        dictionaries such as the visual container properties.
        """
        if hasattr(value, "serialize"):
            return value.serialize()
        if isinstance(value, list):
            return [LayoutNode.serialize_helper(val) for val in value]
        if isinstance(value, dict):
            return {key: LayoutNode.serialize_helper(val) for key, val in value.items()}
        if isinstance(value, Enum):
            return value.name
        return value

    def serialize(self) -> dict[str, Any]:
        """Serialize the node to a dictionary.

        Differs from the model_dump_json method in that it does not convert the JSON models back to strings.
        """
        ret = {}
        for field in self.data_attributes():
            ret[field.name] = self.serialize_helper(getattr(self, field.name))
        return ret

    def pbi_core_name(self) -> str:
        raise NotImplementedError

    @classmethod
    def data_attributes(cls) -> list[Attribute]:
        """Get a list of data attributes for the class.

        This excludes any attributes that are not initialized via the constructor since those are not part of the data
        model. For example, attributes used to link children to parents are excluded since they are only helpers for
        navigation.

        """
        return [field for field in fields(cls) if field.init is True]

    def get_lineage(
        self,
        lineage_type: Literal["children", "parents"],
        tabular_model: "BaseTabularModel",
    ) -> LineageNode:
        raise NotImplementedError
