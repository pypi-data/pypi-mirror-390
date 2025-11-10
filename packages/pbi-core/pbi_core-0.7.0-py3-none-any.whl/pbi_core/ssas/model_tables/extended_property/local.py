import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .extended_property import ExtendedProperty

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalExtendedProperty(ExtendedProperty):
    """Class for an ExtendedProperty that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)
    error_message: str | None = field(default=None, on_setattr=setters.frozen)  # pyright: ignore[reportGeneralTypeIssues]

    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "ExtendedProperty":
        return self._create_helper(ssas, ssas.extended_properties)

    @classmethod
    def _db_type_name(cls) -> str:
        return "ExtendedProperty"
