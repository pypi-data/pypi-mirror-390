import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .linguistic_metadata import LinguisticMetadata

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalLinguisticMetadata(LinguisticMetadata):
    """Class for a LinguisticMetadata that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "LinguisticMetadata":
        return self._create_helper(ssas, ssas.linguistic_metadata)

    @classmethod
    def _db_type_name(cls) -> str:
        return "LinguisticMetadata"
