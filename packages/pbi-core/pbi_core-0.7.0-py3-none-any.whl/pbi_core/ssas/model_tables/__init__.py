import typing

if typing.TYPE_CHECKING:
    from .base import SsasTable

from ._group import Group, RowNotFoundError
from .alternate_of import AlternateOf
from .annotation import Annotation, LocalAnnotation
from .attribute_hierarchy import AttributeHierarchy
from .calc_dependency import CalcDependency
from .calculation_group import CalculationGroup, LocalCalculationGroup
from .calculation_item import CalculationItem, LocalCalculationItem
from .column import Column, LocalColumn
from .column_permission import ColumnPermission, LocalColumnPermission
from .culture import Culture, LocalCulture
from .data_source import DataSource, LocalDataSource
from .detail_row_definition import DetailRowDefinition, LocalDetailRowDefinition
from .expression import Expression, LocalExpression
from .extended_property import ExtendedProperty, LocalExtendedProperty
from .format_string_definition import FormatStringDefinition, LocalFormatStringDefinition
from .group_by_column import GroupByColumn
from .hierarchy import Hierarchy, LocalHierarchy
from .kpi import KPI, LocalKPI
from .level import Level, LocalLevel
from .linguistic_metadata import LinguisticMetadata, LocalLinguisticMetadata
from .measure import LocalMeasure, Measure
from .model import Model
from .object_translation import LocalObjectTranslation, ObjectTranslation
from .partition import LocalPartition, Partition
from .perspective import Perspective
from .perspective_column import PerspectiveColumn
from .perspective_hierarchy import PerspectiveHierarchy
from .perspective_measure import PerspectiveMeasure
from .perspective_set import PerspectiveSet
from .perspective_table import PerspectiveTable
from .query_group import LocalQueryGroup, QueryGroup
from .refresh_policy import LocalRefreshPolicy, RefreshPolicy
from .related_column_detail import RelatedColumnDetail
from .relationship import LocalRelationship, Relationship
from .role import LocalRole, Role
from .role_membership import LocalRoleMembership, RoleMembership
from .set import Set
from .table import LocalTable, Table
from .table_permission import LocalTablePermission, TablePermission
from .variation import LocalVariation, Variation

__all__ = [
    "KPI",
    "AlternateOf",
    "Annotation",
    "AttributeHierarchy",
    "CalcDependency",
    "CalculationGroup",
    "CalculationItem",
    "Column",
    "ColumnPermission",
    "Culture",
    "DataSource",
    "DetailRowDefinition",
    "Expression",
    "ExtendedProperty",
    "FormatStringDefinition",
    "Group",
    "GroupByColumn",
    "Hierarchy",
    "Level",
    "LinguisticMetadata",
    "LocalAnnotation",
    "LocalCalculationGroup",
    "LocalCalculationItem",
    "LocalColumn",
    "LocalColumnPermission",
    "LocalCulture",
    "LocalDataSource",
    "LocalDetailRowDefinition",
    "LocalExpression",
    "LocalExtendedProperty",
    "LocalFormatStringDefinition",
    "LocalHierarchy",
    "LocalKPI",
    "LocalLevel",
    "LocalLinguisticMetadata",
    "LocalMeasure",
    "LocalMeasure",
    "LocalObjectTranslation",
    "LocalPartition",
    "LocalQueryGroup",
    "LocalRefreshPolicy",
    "LocalRelationship",
    "LocalRole",
    "LocalRoleMembership",
    "LocalTable",
    "LocalTablePermission",
    "LocalVariation",
    "Measure",
    "Model",
    "ObjectTranslation",
    "Partition",
    "Perspective",
    "PerspectiveColumn",
    "PerspectiveHierarchy",
    "PerspectiveMeasure",
    "PerspectiveSet",
    "PerspectiveTable",
    "QueryGroup",
    "RefreshPolicy",
    "RelatedColumnDetail",
    "Relationship",
    "Role",
    "RoleMembership",
    "RowNotFoundError",
    "Set",
    "Table",
    "TablePermission",
    "Variation",
]

FIELD_TYPES: dict[str, type["SsasTable"]] = {
    "alternate_ofs": AlternateOf,
    "annotations": Annotation,
    "attribute_hierarchies": AttributeHierarchy,
    "calc_dependencies": CalcDependency,
    "calculation_groups": CalculationGroup,
    "calculation_items": CalculationItem,
    "column_permissions": ColumnPermission,
    "columns": Column,
    "cultures": Culture,
    "data_sources": DataSource,
    "detail_row_definitions": DetailRowDefinition,
    "expressions": Expression,
    "extended_properties": ExtendedProperty,
    "format_string_definitions": FormatStringDefinition,
    "group_by_columns": GroupByColumn,
    "hierarchies": Hierarchy,
    "kpis": KPI,
    "levels": Level,
    "linguistic_metadata": LinguisticMetadata,
    "measures": Measure,
    "model": Model,
    "object_translations": ObjectTranslation,
    "partitions": Partition,
    "perspective_columns": PerspectiveColumn,
    "perspective_hierarchies": PerspectiveHierarchy,
    "perspective_measures": PerspectiveMeasure,
    "perspective_sets": PerspectiveSet,
    "perspective_tables": PerspectiveTable,
    "perspectives": Perspective,
    "query_groups": QueryGroup,
    "relationships": Relationship,
    "refresh_policies": RefreshPolicy,
    "related_column_details": RelatedColumnDetail,
    "role_memberships": RoleMembership,
    "roles": Role,
    "sets": Set,
    "table_permissions": TablePermission,
    "tables": Table,
    "variations": Variation,
}
