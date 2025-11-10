import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import BaseValidation, Json, define
from pbi_core.ssas.model_tables.base import RefreshType, SsasModelRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import ModelCommands

from .enums import DefaultDataView

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import (
        Culture,
        DataSource,
        Expression,
        Measure,
        Perspective,
        QueryGroup,
        Relationship,
        Role,
        Table,
    )


@define()
class DataAccessOptions(BaseValidation):
    fastCombine: bool = field(default=True, eq=True)
    legacyRedirects: bool = field(default=False, eq=True)
    returnErrorValuesAsNull: bool = field(default=False, eq=True)


@define()
class Model(SsasModelRecord):
    """tbd.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/60094cd5-1c7e-4353-9299-251bfa838cc6)
    """

    _default_refresh_type: RefreshType = field(default=RefreshType.CALCULATE, init=False, repr=False, eq=False)

    automatic_aggregation_options: str | None = field(default=None, eq=True)
    collation: str | None = field(default=None, eq=True)
    culture: str = field(eq=True)
    data_access_options: Json[DataAccessOptions] = field(factory=DataAccessOptions, eq=True)
    data_source_default_max_connections: int = field(eq=True)
    data_source_variables_override_behavior: int = field(eq=True)
    default_data_view: DefaultDataView = field(eq=True)
    default_measure_id: int | None = field(default=None, eq=True)
    default_mode: int = field(eq=True)
    default_powerbi_data_source_version: int = field(eq=True)
    description: str | None = field(default=None, eq=True)
    discourage_composite_models: bool = field(default=True, eq=True)
    discourage_implicit_measures: bool = field(default=False, eq=True)
    disable_auto_exists: int | None = field(default=None, eq=True)
    force_unique_names: bool = field(default=False, eq=True)
    m_attributes: str | None = field(default=None, eq=True)
    max_parallelism_per_refresh: int | None = field(default=None, eq=True)
    max_parallelism_per_query: int | None = field(default=None, eq=True)
    name: str = field(eq=True)
    source_query_culture: str = field(default="en-US", eq=True)
    storage_location: str | None = field(default=None, eq=True)
    version: int = field(eq=True)

    modified_time: Final[datetime.datetime] = field(
        eq=False,
        on_setattr=setters.frozen,
        repr=False,
    )
    structure_modified_time: Final[datetime.datetime] = field(
        eq=False,
        on_setattr=setters.frozen,
        repr=False,
    )

    _commands: ModelCommands = field(default=SsasCommands.model, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_MODEL"
    _db_field_names = {
        "id": "ID",
        "automatic_aggregation_options": "AutomaticAggregationOptions",
        "collation": "Collation",
        "culture": "Culture",
        "data_access_options": "DataAccessOptions",
        "data_source_default_max_connections": "DataSourceDefaultMaxConnections",
        "data_source_variables_override_behavior": "DataSourceVariablesOverrideBehavior",
        "default_data_view": "DefaultDataView",
        "default_measure_id": "DefaultMeasureID",
        "default_mode": "DefaultMode",
        "default_powerbi_data_source_version": "DefaultPowerBIDataSourceVersion",
        "description": "Description",
        "discourage_composite_models": "DiscourageCompositeModels",
        "discourage_implicit_measures": "DiscourageImplicitMeasures",
        "disable_auto_exists": "DisableAutoExists",
        "force_unique_names": "ForceUniqueNames",
        "m_attributes": "MAttributes",
        "max_parallelism_per_refresh": "MaxParallelismPerRefresh",
        "max_parallelism_per_query": "MaxParallelismPerQuery",
        "name": "Name",
        "source_query_culture": "SourceQueryCulture",
        "storage_location": "StorageLocation",
        "version": "Version",
        "modified_time": "ModifiedTime",
        "structure_modified_time": "StructureModifiedTime",
    }

    def default_measure(self) -> "Measure | None":
        if self.default_measure_id is None:
            return None
        return self._tabular_model.measures.find(self.default_measure_id)

    def cultures(self) -> set["Culture"]:
        return self._tabular_model.cultures.find_all({"model_id": self.id})

    def data_sources(self) -> set["DataSource"]:
        return self._tabular_model.data_sources.find_all({"model_id": self.id})

    def expressions(self) -> set["Expression"]:
        return self._tabular_model.expressions.find_all({"model_id": self.id})

    def perspectives(self) -> set["Perspective"]:
        return self._tabular_model.perspectives.find_all({"model_id": self.id})

    def query_groups(self) -> set["QueryGroup"]:
        return self._tabular_model.query_groups.find_all({"model_id": self.id})

    def relationships(self) -> set["Relationship"]:
        return self._tabular_model.relationships.find_all({"model_id": self.id})

    def roles(self) -> set["Role"]:
        return self._tabular_model.roles.find_all({"model_id": self.id})

    def tables(self) -> set["Table"]:
        return self._tabular_model.tables.find_all({"model_id": self.id})

    def children_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter(self.annotations(), by="annotation")
            | LinkedEntity.from_iter(self.cultures(), by="culture")
            | LinkedEntity.from_iter(
                self.data_sources(),
                by="data_source",
            )
            | LinkedEntity.from_iter(self.expressions(), by="expression")
            | LinkedEntity.from_iter(
                self.perspectives(),
                by="perspective",
            )
            | LinkedEntity.from_iter(self.query_groups(), by="query_group")
            | LinkedEntity.from_iter(
                self.relationships(),
                by="relationship",
            )
            | LinkedEntity.from_iter(self.roles(), by="role")
            | LinkedEntity.from_iter(self.tables(), by="table")
        )
