from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .refresh_policy import RefreshPolicy

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


# TODO: eventually only subclass from a MeasureDTO to emphasize that you
# shouldn't do most things with this object until it's created in SSAS
# We create a subclass rather than creating a .new method on Measure
# to expose the nice type hinting of the original object and to avoid
# bugs caused by trying to use a LocalMeasure where a Measure is expected.
@define()
class LocalRefreshPolicy(RefreshPolicy):
    """Class for a RefreshPolicy that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    def load(self, ssas: "BaseTabularModel") -> "RefreshPolicy":
        return self._create_helper(ssas, ssas.refresh_policies)

    @classmethod
    def _db_type_name(cls) -> str:
        return "RefreshPolicy"
