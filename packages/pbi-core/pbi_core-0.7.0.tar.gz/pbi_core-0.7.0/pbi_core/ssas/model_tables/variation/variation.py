from typing import TYPE_CHECKING

from attrs import field

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import RenameCommands, SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Hierarchy, Relationship, Table
    from pbi_core.ssas.model_tables.base.ssas_tables import SsasDelete


@define()
class Variation(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/b9dfeb51-cbb6-4eab-91bd-fa2b23f51ca3)
    """

    column_id: int = field(eq=True)
    default_column_id: int | None = field(default=None, eq=True)
    default_hierarchy_id: int = field(eq=True)
    description: str | None = field(default=None, eq=True)
    is_default: bool = field(default=True, eq=True)
    name: str = field(eq=True)
    relationship_id: int = field(eq=True)

    _commands: RenameCommands = field(default=SsasCommands.variation, init=False, repr=False)
    _discover_category: str = "TMSCHEMA_VARIATIONS"
    _db_field_names = {
        "id": "ID",
        "column_id": "ColumnID",
        "default_column_id": "DefaultColumnID",
        "default_hierarchy_id": "DefaultHierarchyID",
        "description": "Description",
        "name": "Name",
        "relationship_id": "RelationshipID",
        "is_default": "IsDefault",
    }

    def column(self) -> "Column":
        """Name is bad to not consistent with other methods because the column field in this entity :(."""
        return self._tabular_model.columns.find(self.column_id)

    def default_column(self) -> "Column | None":
        if self.default_column_id is None:
            return None
        return self._tabular_model.columns.find(self.default_column_id)

    def default_hierarchy(self) -> "Hierarchy":
        return self._tabular_model.hierarchies.find(self.default_hierarchy_id)

    def relationship(self) -> "Relationship":
        return self._tabular_model.relationships.find(self.relationship_id)

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter({self.default_hierarchy()}, by="default_hierarchy")
            | LinkedEntity.from_iter(
                {self.relationship()},
                by="relationship",
            )
            | LinkedEntity.from_iter(
                {self.column()},
                by="column",
            )
            | LinkedEntity.from_iter(
                {self.default_column()},
                by="default_column",
            )
        )

    def delete_objects(self) -> frozenset["SsasDelete"]:
        def table_checker(table: "Table") -> bool:
            if not table.show_as_variations_only:
                return False
            variation_ids = {var.id for var in table.variations()}
            return len(variation_ids - {self.id}) == 0

        """Returns a set of dependent objects that should be deleted before/while this object is deleted."""
        ret: set[SsasDelete] = set({self})
        if source_table := self._tabular_model.tables.find(table_checker):
            ret.update(source_table.delete_objects())
        return frozenset(ret)
