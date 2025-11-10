from typing import TYPE_CHECKING

from attrs import field

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Expression, Model, Partition
    from pbi_core.ssas.model_tables.base.ssas_tables import SsasDelete


@define()
class QueryGroup(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/40b3830b-25ee-41a6-87d2-49616028dd13)
    This class represents a group of queries that can be executed together.
    """

    _repr_name_field: str = field(default="folder")

    description: str | None = field(default=None, eq=True)
    folder: str = field(eq=True)
    model_id: int = field(eq=True)

    _commands: BaseCommands = field(default=SsasCommands.query_group, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_QUERY_GROUPS"
    _db_field_names = {"id": "ID", "model_id": "ModelID", "folder": "Folder"}

    def expressions(self) -> set["Expression"]:
        return self._tabular_model.expressions.find_all({"query_group_id": self.id})

    def partitions(self) -> set["Partition"]:
        return self._tabular_model.partitions.find_all({"query_group_id": self.id})

    def model(self) -> "Model":
        return self._tabular_model.model

    def children_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter(self.expressions(), by="expression")
            | LinkedEntity.from_iter(
                self.partitions(),
                by="partition",
            )
            | LinkedEntity.from_iter(
                self.annotations(),
                by="annotation",
            )
        )

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.model()}, by="model")

    def delete_objects(self) -> frozenset["SsasDelete"]:
        base = {self}
        for obj in self.expressions():
            base |= obj.delete_objects()
        for obj in self.partitions():
            base |= obj.delete_objects()
        return frozenset(base)
