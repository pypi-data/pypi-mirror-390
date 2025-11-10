import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.enums.enums import DataType

from .measure import Measure

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


# TODO: eventually only subclass from a MeasureDTO to emphasize that you
# shouldn't do most things with this object until it's created in SSAS
# We create a subclass rather than creating a .new method on Measure
# to expose the nice type hinting of the original object and to avoid
# bugs caused by trying to use a LocalMeasure where a Measure is expected.
@define()
class LocalMeasure(Measure):
    """Class for a Measure that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)
    # The datatype will be inferred by SSAS on creation
    data_type: DataType = DataType.UNKNOWN
    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )
    structure_modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "Measure":
        return self._create_helper(ssas, ssas.measures)

    @classmethod
    def _db_type_name(cls) -> str:
        return "Measure"
