import datetime
from enum import Enum
from typing import TYPE_CHECKING, Final
from uuid import UUID, uuid4

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import RenameCommands, SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Model, QueryGroup


class Kind(Enum):
    M = 0


@define()
class Expression(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/61f98e45-d5e3-4435-b829-2f2f043839c1)
    """

    description: str | None = field(default=None, eq=True)
    expression: str = field(eq=True)
    kind: Kind = field(eq=True, default=Kind.M)
    model_id: Final[int] = field(eq=False)
    name: str = field(eq=True)
    parameter_values_column_id: int | None = field(default=None, eq=True)
    query_group_id: int | None = field(default=None, eq=True)

    lineage_tag: UUID = field(factory=uuid4, eq=True, repr=False)
    source_lineage_tag: UUID = field(factory=uuid4, eq=True, repr=False)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.expression, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_EXPRESSIONS"
    _db_field_names = {
        "id": "ID",
        "model_id": "ModelID",
        "name": "Name",
        "kind": "Kind",
        "expression": "Expression",
        "modified_time": "ModifiedTime",
        "lineage_tag": "LineageTag",
    }

    def model(self) -> "Model":
        return self._tabular_model.model

    def parameter_values_column(self) -> "Column | None":
        if self.parameter_values_column_id is None:
            return None
        return self._tabular_model.columns.find(self.parameter_values_column_id)

    def query_group(self) -> "QueryGroup | None":
        if self.query_group_id is None:
            return None
        return self._tabular_model.query_groups.find({"id": self.query_group_id})

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter({self.model()}, by="model")
            | LinkedEntity.from_iter({self.query_group()}, by="query_group")
            | LinkedEntity.from_iter(
                {self.parameter_values_column()},
                by="parameter_values_column",
            )
        )
