import datetime
from typing import TYPE_CHECKING, Final
from uuid import UUID, uuid4

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import RenameCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Hierarchy


@define()
class Level(SsasRenameRecord):
    """A level in a hierarchy. For example, in a hierarchy of "Date", the levels could be "Year", "Month", and "Day".

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/a010d75e-3b68-4825-898f-62fdeab4557f)
    """

    column_id: int = field(eq=True)
    description: str | None = field(default=None, eq=True)
    """A description of the level, which may be used in the hover tooltip in edit mode"""
    hierarchy_id: int = field(eq=True)
    name: str = field(eq=True)
    """The name of the level, e.g. "Year", "Quarter", "Month", "Day" in a Date hierarchy."""
    ordinal: int = field(default=0, eq=True)

    lineage_tag: UUID = field(factory=uuid4, eq=True, repr=False)
    source_lineage_tag: UUID = field(factory=uuid4, eq=True, repr=False)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.level, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_LEVELS"
    _db_field_names = {
        "id": "ID",
        "hierarchy_id": "HierarchyID",
        "ordinal": "Ordinal",
        "name": "Name",
        "column_id": "ColumnID",
        "modified_time": "ModifiedTime",
        "lineage_tag": "LineageTag",
    }

    def column(self) -> "Column":
        return self._tabular_model.columns.find({"id": self.column_id})

    def hierarchy(self) -> "Hierarchy":
        return self._tabular_model.hierarchies.find({"id": self.hierarchy_id})

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.column()}, by="column") | LinkedEntity.from_iter(
            {self.hierarchy()},
            by="hierarchy",
        )

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")
