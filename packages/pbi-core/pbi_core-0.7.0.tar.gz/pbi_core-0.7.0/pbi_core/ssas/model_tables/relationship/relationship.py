import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.logging import get_logger
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import RenameCommands

from .enums import (
    CrossFilteringBehavior,
    FromCardinality,
    JoinOnDateBehavior,
    RelationshipType,
    SecurityFilteringBehavior,
    ToCardinality,
)

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Model, Table, Variation
    from pbi_core.ssas.model_tables.base.ssas_tables import SsasDelete

logger = get_logger()


@define()
class Relationship(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/35bb4a68-b97e-409b-a5dd-14695fd99139)
    This class represents a relationship between two tables in a Tabular model.
    """

    cross_filtering_behavior: CrossFilteringBehavior = field(default=CrossFilteringBehavior.ONE_DIRECTION, eq=True)
    from_column_id: int = field(eq=True)
    from_cardinality: FromCardinality = field(default=FromCardinality.ONE, eq=True)
    from_table_id: int = field(eq=True)
    is_active: bool = field(default=True, eq=True)
    join_on_date_behavior: JoinOnDateBehavior = field(default=JoinOnDateBehavior.DATE_PART_ONLY, eq=True)
    model_id: int = field(eq=True)
    name: str = field(eq=True)
    relationship_storage_id: int | None = field(eq=True, default=None)
    relationship_storage2_id: int | None = field(eq=True, default=None)
    """wtf these are two different fields in the json??!!??"""
    relationship_storage2id: int | None = field(eq=True, default=None)
    """wtf these are two different fields in the json??!!??"""
    rely_on_referential_integrity: bool = field(default=False, eq=True)
    security_filtering_behavior: SecurityFilteringBehavior = field(
        default=SecurityFilteringBehavior.ONE_DIRECTION,
        eq=True,
    )
    state: Final[DataState] = field(eq=False, on_setattr=setters.frozen, default=DataState.READY)
    to_cardinality: ToCardinality = field(default=ToCardinality.MANY, eq=True)
    to_column_id: int = field(eq=True)
    to_table_id: int = field(eq=True)
    type: RelationshipType = field(default=RelationshipType.SINGLE_COLUMN, eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)
    refreshed_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.relationship, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_RELATIONSHIPS"
    _db_field_names = {
        "id": "ID",
        "model_id": "ModelID",
        "name": "Name",
        "is_active": "IsActive",
        "type": "Type",
        "cross_filtering_behavior": "CrossFilteringBehavior",
        "join_on_date_behavior": "JoinOnDateBehavior",
        "rely_on_referential_integrity": "RelyOnReferentialIntegrity",
        "from_table_id": "FromTableID",
        "from_column_id": "FromColumnID",
        "from_cardinality": "FromCardinality",
        "to_table_id": "ToTableID",
        "to_column_id": "ToColumnID",
        "to_cardinality": "ToCardinality",
        "state": "State",
        "relationship_storage_id": "RelationshipStorageID",
        "modified_time": "ModifiedTime",
        "refreshed_time": "RefreshedTime",
        "security_filtering_behavior": "SecurityFilteringBehavior",
    }

    def from_table(self) -> "Table":
        """Returns the table the relationship is using as a filter.

        Note:
            In the bi-directional case, this table is also filtered

        """
        return self._tabular_model.tables.find({"id": self.from_table_id})

    def to_table(self) -> "Table":
        """Returns the table the relationship is being filtered.

        Note:
            In the bi-directional case, this table is also used as a filter

        """
        return self._tabular_model.tables.find({"id": self.to_table_id})

    def from_column(self) -> "Column":
        """The column in the from_table used to join with the to_table."""
        return self._tabular_model.columns.find({"id": self.from_column_id})

    def to_column(self) -> "Column":
        """The column in the to_table used to join with the from_table."""
        return self._tabular_model.columns.find({"id": self.to_column_id})

    def model(self) -> "Model":
        """The DB model this entity exists in."""
        return self._tabular_model.model

    def variations(self) -> set["Variation"]:
        return self._tabular_model.variations.find_all({"relationship_id": self.id})

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.variations(), by="variation") | LinkedEntity.from_iter(
            self.annotations(),
            by="annotation",
        )

    def parents_base(self) -> frozenset["LinkedEntity"]:
        """Returns all tables and columns this Relationship is dependent on.

        Note:
            Although relationships have direct links to tables via the from_table_id and to_table_id,
            they are actually dependent on the columns that make up those tables. Therefore, `recursive=False`
            returns only the from_column and to_column as dependencies.

        """
        return LinkedEntity.from_iter({self.from_column()}, by="from_column") | LinkedEntity.from_iter(
            {self.to_column()},
            by="to_column",
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, from: {self.pbi_core_name()}, to: {self.pbi_core_name()})"

    def delete_objects(self) -> frozenset["SsasDelete"]:
        """Returns a set of dependent objects that should be deleted before/while this object is deleted."""
        ret: set[SsasDelete] = set({self})
        for variation in self.variations():
            ret.update(variation.delete_objects())
        return frozenset(ret)
