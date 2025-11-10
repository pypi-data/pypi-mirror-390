import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import (
        Perspective,
        PerspectiveColumn,
        PerspectiveHierarchy,
        PerspectiveMeasure,
        Table,
    )


@define()
class PerspectiveTable(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/06bc5956-20e3-4bd2-8e5f-68a200efc18b)
    """

    include_all: bool = field(eq=True)
    perspective_id: int = field(eq=True)
    table_id: int = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: BaseCommands = field(default=SsasCommands.perspective_table, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_PERSPECTIVE_TABLES"
    _db_field_names = {}

    def perspective(self) -> "Perspective":
        return self._tabular_model.perspectives.find(self.perspective_id)

    def table(self) -> "Table":
        return self._tabular_model.tables.find(self.table_id)

    def perspective_columns(self) -> set["PerspectiveColumn"]:
        return self._tabular_model.perspective_columns.find_all({"perspective_table_id": self.id})

    def perspective_hierarchies(self) -> set["PerspectiveHierarchy"]:
        return self._tabular_model.perspective_hierarchies.find_all({"perspective_table_id": self.id})

    def perspective_measures(self) -> set["PerspectiveMeasure"]:
        return self._tabular_model.perspective_measures.find_all({"perspective_table_id": self.id})

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.perspective()}, by="perspective") | LinkedEntity.from_iter(
            {self.table()},
            by="table",
        )

    def children_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter(self.perspective_columns(), by="perspective_column")
            | LinkedEntity.from_iter(
                self.perspective_hierarchies(),
                by="perspective_hierarchy",
            )
            | LinkedEntity.from_iter(
                self.perspective_measures(),
                by="perspective_measure",
            )
            | LinkedEntity.from_iter(
                self.annotations(),
                by="annotation",
            )
        )
