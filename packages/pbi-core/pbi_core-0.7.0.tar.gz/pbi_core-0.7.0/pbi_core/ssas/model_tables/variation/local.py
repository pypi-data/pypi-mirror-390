from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .variation import Variation

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalVariation(Variation):
    """Class for a Variation that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    def load(self, ssas: "BaseTabularModel") -> "Variation":
        return self._create_helper(ssas, ssas.variations)

    @classmethod
    def _db_type_name(cls) -> str:
        return "Variation"
