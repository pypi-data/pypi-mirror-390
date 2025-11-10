from typing import TYPE_CHECKING

from attrs import field

from pbi_core.attrs import define
from pbi_core.logging import get_logger
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import RenameCommands, SsasCommands
from pbi_core.static_files.layout.filters import Filter
from pbi_core.static_files.layout.sources.base import Entity, Source, SourceRef
from pbi_core.static_files.layout.sources.column import ColumnSource
from pbi_core.static_files.layout.sources.hierarchy import HierarchySource, _PropertyVariationSourceHelper
from pbi_core.static_files.layout.visuals.base import BaseVisual

from . import set_name
from .commands import CommandMixin

if TYPE_CHECKING:
    from pbi_core.static_files.layout import Layout, LayoutNode

logger = get_logger()


@define()
class Column(CommandMixin, SsasRenameRecord):  # pyright: ignore[reportIncompatibleMethodOverride]
    """A column of an SSAS table.

    PowerBI spec: [Power BI](https://learn.microsoft.com/en-us/analysis-services/tabular-models/column-properties-ssas-tabular?view=asallproducts-allversions)

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/00a9ec7a-5f4d-4517-8091-b370fe2dc18b)
    """

    _commands: RenameCommands = field(default=SsasCommands.column, init=False, repr=False)
    _discover_category: str = "TMSCHEMA_COLUMNS"
    _db_field_names = {
        "id": "ID",
        "table_id": "TableID",
        "inferred_name": "InferredName",
        "explicit_name": "ExplicitName",
        "data_category": "DataCategory",
        "source_column": "SourceColumn",
        "explicit_data_type": "ExplicitDataType",
        "inferred_data_type": "InferredDataType",
        "is_hidden": "IsHidden",
        "state": "State",
        "is_unique": "IsUnique",
        "is_key": "IsKey",
        "is_nullable": "IsNullable",
        "alignment": "Alignment",
        "table_detail_position": "TableDetailPosition",
        "is_default_label": "IsDefaultLabel",
        "is_default_image": "IsDefaultImage",
        "lineage_tag": "LineageTag",
        "source_lineage_tag": "SourceLineageTag",
        "description": "Description",
        "expression": "Expression",
        "sort_by_column_id": "SortByColumnID",
        "format_string": "FormatString",
        "summarize_by": "SummarizeBy",
        "format_string_definition_id": "FormatStringDefinitionID",
        "column_storage_id": "ColumnStorageID",
        "type": "Type",
        "is_available_in_mdx": "IsAvailableInMDX",
        "attribute_hierarchy_id": "AttributeHierarchyID",
        "modified_time": "ModifiedTime",
        "structure_modified_time": "StructureModifiedTime",
        "refreshed_time": "RefreshedTime",
        "system_flags": "SystemFlags",
        "keep_unique_rows": "KeepUniqueRows",
        "display_ordinal": "DisplayOrdinal",
        "encoding_hint": "EncodingHint",
    }

    def __repr__(self) -> str:
        return f"Column({self.id}: {self.full_name()})"

    def parents_base(self) -> "frozenset[LinkedEntity]":
        """Returns all columns and measures this Column is dependent on."""
        return (
            LinkedEntity.from_iter({self.table()}, by="table")
            | LinkedEntity.from_iter(
                self.parent_columns(),
                by="parent_column",
            )
            | LinkedEntity.from_iter(self.parent_measures(), by="parent_measure")
            | LinkedEntity.from_iter({self.sort_by_column()}, by="sort_by_column")
            | LinkedEntity.from_iter({self.column_origin()}, by="column_origin")
        )

    def children_base(self) -> "frozenset[LinkedEntity]":
        """Returns all columns and measures dependent on this Column."""
        return (
            LinkedEntity.from_iter(self.annotations(), by="annotation")
            | LinkedEntity.from_iter({self.attribute_hierarchy()}, by="attribute_hierarchy")
            | LinkedEntity.from_iter(
                self.child_columns(),
                by="child_column",
            )
            | LinkedEntity.from_iter(self.child_measures(), by="child_measure")
            | LinkedEntity.from_iter(
                self.origin_columns(),
                by="origin_column",
            )
            | LinkedEntity.from_iter(self.sorting_columns(), by="sorting_column")
            | LinkedEntity.from_iter(
                self.child_variations(),
                by="child_variation",
            )
            | LinkedEntity.from_iter(
                self.child_default_variations(),
                by="child_default_variation",
            )
            | LinkedEntity.from_iter(self.from_relationships(), by="from_relationship")
            | LinkedEntity.from_iter(
                self.to_relationships(),
                by="to_relationship",
            )
            | LinkedEntity.from_iter(self.perspective_columns(), by="perspective_column")
            | LinkedEntity.from_iter({self.format_string_definition()}, by="format_string_definition")
        )

    def set_name(self, new_name: str, layout: "Layout") -> None:
        """Renames the column and update any dependent expressions to use the new name.

        Since measures are referenced by name in DAX expressions, renaming a measure will break any dependent
        expressions.
        """
        columns = _get_columns_sources(self, layout)
        for c in columns:
            c.Column.Property = new_name
            if c.NativeReferenceName == self.name():
                c.NativeReferenceName = new_name
        hierarchies = _get_hierarchies_sources(self, layout)
        for h in hierarchies:
            if isinstance(h.Hierarchy.Expression, SourceRef):
                h.Hierarchy.Hierarchy = new_name
            elif isinstance(h.Hierarchy.Expression, _PropertyVariationSourceHelper):
                h.Hierarchy.Expression.PropertyVariationSource.Property = new_name
            else:
                h.Hierarchy.Hierarchy = new_name
        set_name.fix_dax(self, new_name)
        self.explicit_name = new_name


def _get_matching_columns(n: "LayoutNode", entity_mapping: dict[str, str], column: "Column") -> list[ColumnSource]:
    columns = []
    for c in n.find_all(ColumnSource):
        if c.Column.Property != column.name():
            continue

        if isinstance(c.Column.Expression, SourceRef):
            src = c.Column.Expression.SourceRef
        else:
            src = c.Column.Expression.TransformTableRef

        if isinstance(src, Source):
            if entity_mapping[src.Source] == column.table().name:
                columns.append(c)
        elif src.Entity == column.table().name:
            columns.append(c)

    return columns


def _get_columns_sources(column: "Column", layout: "Layout") -> list[ColumnSource]:
    columns = []
    visuals = layout.find_all(BaseVisual)
    for v in visuals:
        if v.prototypeQuery is None:
            continue
        entity_mapping = {
            e.Name: e.Entity for e in v.prototypeQuery.From if isinstance(e, Entity) and e.Name is not None
        }
        columns.extend(_get_matching_columns(v, entity_mapping, column))

    filters = layout.find_all(Filter)
    for f in filters:
        entity_mapping = {}
        if f.filter is not None:
            entity_mapping = {e.Name: e.Entity for e in f.filter.From if isinstance(e, Entity) and e.Name is not None}
        columns.extend(_get_matching_columns(f, entity_mapping, column))
    return columns


def _get_matching_hierarchies(
    n: "LayoutNode",
    entity_mapping: dict[str, str],
    column: "Column",
) -> list[HierarchySource]:
    hierarchies = []

    for h in n.find_all(HierarchySource):
        if isinstance(h.Hierarchy.Expression, SourceRef):
            table_name = h.Hierarchy.Expression.table(entity_mapping)
            column_name = h.Hierarchy.Hierarchy
        if isinstance(h.Hierarchy.Expression, _PropertyVariationSourceHelper):
            table_name = h.Hierarchy.Expression.PropertyVariationSource.Expression.table(entity_mapping)
            column_name = h.Hierarchy.Expression.PropertyVariationSource.Property
        else:
            table_name = h.Hierarchy.Expression.table(entity_mapping)
            column_name = h.Hierarchy.Hierarchy

        if column_name == column.name() and table_name == column.table().name:
            hierarchies.append(h)
    return hierarchies


def _get_hierarchies_sources(column: "Column", layout: "Layout") -> list[HierarchySource]:
    hierarchies = []
    visuals = layout.find_all(BaseVisual)
    for v in visuals:
        if v.prototypeQuery is None:
            continue
        entity_mapping = {
            e.Name: e.Entity for e in v.prototypeQuery.From if isinstance(e, Entity) and e.Name is not None
        }
        hierarchies.extend(_get_matching_hierarchies(v, entity_mapping, column))

    return hierarchies
