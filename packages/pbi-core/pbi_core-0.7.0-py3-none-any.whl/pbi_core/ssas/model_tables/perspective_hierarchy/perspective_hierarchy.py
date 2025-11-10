import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Hierarchy, PerspectiveTable


@define()
class PerspectiveHierarchy(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/07941935-98bf-4e14-ab40-ef97d5c29765)
    """

    hierarchy_id: int = field(eq=True)
    perspective_table_id: int = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: BaseCommands = field(
        default=SsasCommands.perspective_hierarchy,
        init=False,
        repr=False,
        eq=False,
    )
    _discover_category: str = "TMSCHEMA_PERSPECTIVE_HIERARCHIES"
    _db_field_names = {}

    def perspective_table(self) -> "PerspectiveTable":
        return self._tabular_model.perspective_tables.find(self.perspective_table_id)

    def hierarchy(self) -> "Hierarchy":
        return self._tabular_model.hierarchies.find(self.hierarchy_id)

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.perspective_table()}, by="perspective_table") | LinkedEntity.from_iter(
            {self.hierarchy()},
            by="hierarchy",
        )
