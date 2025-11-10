import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .format_string_definition import FormatStringDefinition

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalFormatStringDefinition(FormatStringDefinition):
    """Class for a Measure that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)
    object_id: int = field(default=-1)  # pyright: ignore[reportIncompatibleVariableOverride]
    # The datatype will be inferred by SSAS on creation
    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "FormatStringDefinition":
        return self._create_helper(ssas, ssas.format_string_definitions)

    @classmethod
    def _db_type_name(cls) -> str:
        return "FormatStringDefinition"
