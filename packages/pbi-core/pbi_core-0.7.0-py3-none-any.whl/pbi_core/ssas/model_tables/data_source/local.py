import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define

from .data_source import DataSource

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalDataSource(DataSource):
    """Class for a DataSource that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)

    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )
    structure_modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "DataSource":
        return self._create_helper(ssas, ssas.data_sources)

    @classmethod
    def _db_type_name(cls) -> str:
        return "DataSource"
