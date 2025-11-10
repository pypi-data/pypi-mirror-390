from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .query_group import QueryGroup

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


# TODO: eventually only subclass from a MeasureDTO to emphasize that you
# shouldn't do most things with this object until it's created in SSAS
# We create a subclass rather than creating a .new method on Measure
# to expose the nice type hinting of the original object and to avoid
# bugs caused by trying to use a LocalMeasure where a Measure is expected.
@define()
class LocalQueryGroup(QueryGroup):
    """Class for a QueryGroup that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    def load(self, ssas: "BaseTabularModel") -> "QueryGroup":
        return self._create_helper(ssas, ssas.query_groups)

    @classmethod
    def _db_type_name(cls) -> str:
        return "QueryGroup"
