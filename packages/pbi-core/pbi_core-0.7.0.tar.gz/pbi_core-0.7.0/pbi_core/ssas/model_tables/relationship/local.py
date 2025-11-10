import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .relationship import Relationship

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


# TODO: eventually only subclass from a MeasureDTO to emphasize that you
# shouldn't do most things with this object until it's created in SSAS
# We create a subclass rather than creating a .new method on Measure
# to expose the nice type hinting of the original object and to avoid
# bugs caused by trying to use a LocalMeasure where a Measure is expected.
@define()
class LocalRelationship(Relationship):
    """Class for a Relationship that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)
    relationship_storage_id: int = field(default=-1, on_setattr=setters.frozen)  # pyright: ignore[reportIncompatibleVariableOverride]
    relationship_storage2_id: int = field(default=-1, on_setattr=setters.frozen)  # pyright: ignore[reportIncompatibleVariableOverride]
    relationship_storage2id: int = field(default=-1, on_setattr=setters.frozen)  # pyright: ignore[reportIncompatibleVariableOverride]
    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )
    refreshed_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "Relationship":
        return self._create_helper(ssas, ssas.relationships)

    @classmethod
    def _db_type_name(cls) -> str:
        return "Relationship"
