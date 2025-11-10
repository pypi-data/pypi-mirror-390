import copy
import pathlib
import shutil
from typing import TYPE_CHECKING, Any, cast

import bs4
from attrs import define, field, fields
from structlog import get_logger

from pbi_core.ssas.server.utils import COMMAND_TEMPLATES
from pbi_core.ssas.trace import PerformanceTrace

logger = get_logger()
if TYPE_CHECKING:
    from _typeshed import StrPath

    from pbi_core.ssas.model_tables import (
        KPI,
        AlternateOf,
        Annotation,
        AttributeHierarchy,
        CalcDependency,
        CalculationGroup,
        CalculationItem,
        Column,
        ColumnPermission,
        Culture,
        DataSource,
        DetailRowDefinition,
        Expression,
        ExtendedProperty,
        FormatStringDefinition,
        Group,
        GroupByColumn,
        Hierarchy,
        Level,
        LinguisticMetadata,
        Measure,
        Model,
        ObjectTranslation,
        Partition,
        Perspective,
        PerspectiveColumn,
        PerspectiveHierarchy,
        PerspectiveMeasure,
        PerspectiveSet,
        PerspectiveTable,
        QueryGroup,
        RefreshPolicy,
        RelatedColumnDetail,
        Relationship,
        Role,
        RoleMembership,
        Set,
        SsasTable,
        Table,
        TablePermission,
        Variation,
    )
    from pbi_core.ssas.model_tables.base.ssas_tables import SsasAlter
    from pbi_core.ssas.server._commands import CommandData
    from pbi_core.ssas.server.server import BaseServer, LocalServer


@define()
class Update:
    added: list["SsasTable"] = field(factory=list)
    updated: list["SsasAlter"] = field(factory=list)
    deleted: list[int] = field(factory=list)


@define(init=False)
class BaseTabularModel:
    db_name: str
    server: "BaseServer"
    model: "Model"

    alternate_ofs: "Group[AlternateOf]"
    annotations: "Group[Annotation]"
    """Notes that can be attached to a variety other SSAS objects"""

    attribute_hierarchies: "Group[AttributeHierarchy]"
    calc_dependencies: "Group[CalcDependency]"
    """Returns all (multi-generational) ancestors of a calculation element"""
    calculation_groups: "Group[CalculationGroup]"
    calculation_items: "Group[CalculationItem]"
    columns: "Group[Column]"
    """Columns include source (MQuery) and calculate columns from tables"""

    column_permissions: "Group[ColumnPermission]"
    cultures: "Group[Culture]"
    data_sources: "Group[DataSource]"
    detail_row_definitions: "Group[DetailRowDefinition]"
    expressions: "Group[Expression]"
    extended_properties: "Group[ExtendedProperty]"
    format_string_definitions: "Group[FormatStringDefinition]"
    group_by_columns: "Group[GroupByColumn]"
    hierarchies: "Group[Hierarchy]"
    kpis: "Group[KPI]"
    levels: "Group[Level]"
    linguistic_metadata: "Group[LinguisticMetadata]"
    measures: "Group[Measure]"
    object_translations: "Group[ObjectTranslation]"
    partitions: "Group[Partition]"
    """Partitions are generally accessed to edit the Power Query of a Table"""

    perspectives: "Group[Perspective]"
    perspective_columns: "Group[PerspectiveColumn]"
    perspective_hierarchies: "Group[PerspectiveHierarchy]"
    perspective_measures: "Group[PerspectiveMeasure]"
    perspective_sets: "Group[PerspectiveSet]"
    perspective_tables: "Group[PerspectiveTable]"
    query_groups: "Group[QueryGroup]"
    refresh_policies: "Group[RefreshPolicy]"
    related_column_details: "Group[RelatedColumnDetail]"
    relationships: "Group[Relationship]"
    roles: "Group[Role]"
    role_memberships: "Group[RoleMembership]"
    sets: "Group[Set]"
    tables: "Group[Table]"
    """This class contains the logical elements of a PowerBI table"""

    table_permissions: "Group[TablePermission]"
    variations: "Group[Variation]"

    def __init__(self, db_name: str, server: "BaseServer") -> None:
        self.db_name = db_name
        self.server = server

    def save_pbix(self, path: "StrPath") -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"TabularModel(db_name={self.db_name}, server={self.server})"

    def to_local(self, pbix_path: pathlib.Path) -> "LocalTabularModel":
        server = cast("LocalServer", self.server)
        return LocalTabularModel(self.db_name, server, pbix_path)

    def sync_from(self) -> None:
        """Pulls data from the SSAS instance to the Python instance.

        Pairs with the functions `sync_to` that update records in the
        SSAS instance with data from Python
        """
        logger.info("Syncing from SSAS", db_name=self.db_name)
        from pbi_core.ssas.model_tables import FIELD_TYPES  # noqa: PLC0415
        from pbi_core.ssas.model_tables._group import Group  # noqa: PLC0415

        xml_schema = self.server.query_xml(COMMAND_TEMPLATES["discover_schema.xml"].render(db_name=self.db_name))
        schema = discover_xml_to_dict(xml_schema)
        for field_name, type_instance in FIELD_TYPES.items():
            field_data = schema[type_instance._db_type_name()]

            group = []
            for row in field_data:
                e = type_instance.model_validate(row)
                e._original_data = copy.copy(e)
                e._tabular_model = self
                group.append(e)

            if field_name == "model":
                setattr(self, field_name, group[0])
            else:
                setattr(self, field_name, Group(group))

    def sync_to(self) -> Update:
        from pbi_core.ssas.model_tables.base.ssas_tables import SsasAlter, SsasTable  # noqa: PLC0415
        from pbi_core.ssas.server.batch import Batch  # noqa: PLC0415

        logger.info("Syncing to SSAS", db_name=self.db_name)
        updated_objects: dict[str, Update] = {}
        for f in fields(self.__class__):
            field_updates: Update = Update()
            current_objects: Any = getattr(self, f.name)
            if isinstance(current_objects, SsasTable):
                current_objects = [current_objects]
            elif not isinstance(current_objects, list):
                continue

            for obj in current_objects:
                if obj.get_altered_fields() and isinstance(obj, SsasAlter):
                    field_updates.updated.append(obj)
            if field_updates.added or field_updates.updated or field_updates.deleted:
                updated_objects[f.name] = field_updates

        commands: list[CommandData] = [
            update.alter_cmd() for updates in updated_objects.values() for update in updates.updated
        ]

        command_str = Batch(commands=commands).render_xml()
        self.server.query_xml(command_str, db_name=self.db_name)
        logger.info(
            "Completed sync to SSAS",
            added=sum(len(v.added) for v in updated_objects.values()),
            updated=sum(len(v.updated) for v in updated_objects.values()),
            deleted=sum(len(v.deleted) for v in updated_objects.values()),
        )
        return Update(
            added=[obj for updates in updated_objects.values() for obj in updates.added],
            updated=[obj for updates in updated_objects.values() for obj in updates.updated],
            deleted=[obj_id for updates in updated_objects.values() for obj_id in updates.deleted],
        )

    @classmethod
    def TABULAR_FIELDS(cls) -> tuple[str, ...]:  # noqa: N802
        """Returns a list of all the field names for the SSAS tables in the tabular model.

        No calc_dependencies, it's not a real table but a view
        No model, since it's not a "real" table
        """
        blacklist = {"calc_dependencies", "model", "db_name", "server"}
        return tuple(f.name for f in fields(cls) if f.name not in blacklist)

    def get_performance_trace(self) -> PerformanceTrace:
        """Returns a performance trace for this tabular model instance.

        This trace can be used to analyze performance of DAX queries against this model.
        """
        return PerformanceTrace(self)


class LocalTabularModel(BaseTabularModel):
    pbix_path: pathlib.Path
    server: "LocalServer"  # type: ignore[assignment]

    def __init__(self, db_name: str, server: "LocalServer", pbix_path: pathlib.Path) -> None:
        # Without absolute, saving the PBIX after changing working directories can fail
        self.pbix_path = pbix_path.absolute()
        super().__init__(db_name, server)

    def save_pbix(self, path: "StrPath") -> None:
        shutil.copy(self.pbix_path, path)
        self.server.save_pbix(path, self.db_name)  # pyright: ignore reportAttributeAccessIssue  # the server is always a local server in this case


def parse_schema(xml: bs4.BeautifulSoup) -> dict[str, str | int]:
    schema = {}
    for prop in xml.find("xsd:complexType", {"name": "row"}).find_all("xsd:element"):  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]
        if prop["type"] in {"xsd:unsignedLong", "xsd:int", "xsd:long"}:  # pyright: ignore[reportArgumentType, reportIndexIssue]
            schema[prop["name"]] = int  # pyright: ignore[reportIndexIssue, reportArgumentType]
        elif prop["type"] == "xsd:boolean":  # pyright: ignore[reportArgumentType, reportIndexIssue]
            schema[prop["name"]] = lambda b: b == "true"  # pyright: ignore[reportIndexIssue, reportArgumentType]
    return schema


def discover_xml_to_dict(xml: bs4.BeautifulSoup) -> dict[str, list[dict[Any, Any]]]:
    """Converts the results of the Discover XML to a dictionary to make downstream transformations more convenient.

    Args:
        xml (bs4.BeautifulSoup): The XML returned from a Discover command.

    Returns:
        dict[str, list[dict[Any, Any]]]: A dictionary mapping table names to lists of row dictionaries.

    """
    assert xml.results is not None
    results = cast("list[bs4.element.Tag]", list(xml.results))
    if "name" not in results[-1].attrs:
        results[-1]["name"] = "CalcDependency"

    ret = {}
    for table in results:
        schema = parse_schema(table)  # pyright: ignore[reportArgumentType]
        name: str = table["name"]  # pyright: ignore[reportAssignmentType]
        table_results = [
            {field.name: schema.get(field.name, lambda x: x)(field.text) for field in row if field.name is not None}  # pyright: ignore reportGeneralTypeIssues
            for row in table.find_all("row")
        ]

        ret[name] = table_results
    if "CalcDependency" in ret:
        for i, row in enumerate(ret["CalcDependency"]):
            row["id"] = i
    return ret
