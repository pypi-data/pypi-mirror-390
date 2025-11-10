import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .object_translation import ObjectTranslation

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


# TODO: eventually only subclass from a MeasureDTO to emphasize that you
# shouldn't do most things with this object until it's created in SSAS
# We create a subclass rather than creating a .new method on Measure
# to expose the nice type hinting of the original object and to avoid
# bugs caused by trying to use a LocalMeasure where a Measure is expected.
@define()
class LocalObjectTranslation(ObjectTranslation):
    """Class for a ObjectTranslation that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "ObjectTranslation":
        return self._create_helper(ssas, ssas.object_translations)

    @classmethod
    def _db_type_name(cls) -> str:
        return "ObjectTranslation"
