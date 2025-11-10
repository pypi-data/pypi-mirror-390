from typing import TYPE_CHECKING

from pbi_core.ssas.model_tables._group import RowNotFoundError
from pbi_core.ssas.model_tables.base import SsasTable

from .base import ColumnDTO

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import (
        AttributeHierarchy,
        Column,
        FormatStringDefinition,
        Level,
        PerspectiveColumn,
        Relationship,
        Table,
    )


class RelationshipMixin(ColumnDTO, SsasTable):
    def table(self) -> "Table":
        """Returns the table class the column is a part of."""
        return self._tabular_model.tables.find({"id": self.table_id})

    def attribute_hierarchy(self) -> "AttributeHierarchy":
        return self._tabular_model.attribute_hierarchies.find({"id": self.attribute_hierarchy_id})

    def levels(self) -> set["Level"]:
        return self._tabular_model.levels.find_all({"column_id": self.id})

    def sort_by_column(self) -> "Column | None":
        """Returns the column (if any) that is used to sort this column.

        Note:
            This is the inverse of sorting_columns

        """
        if self.sort_by_column_id is None:
            return None
        return self._tabular_model.columns.find({"id": self.sort_by_column_id})

    def column_origin(self) -> "Column | None":
        """Returns the origin column (if any) for this column.

        Note:
            This is the inverse of origin_columns

        """
        if self.column_origin_id is None:
            return None
        return self._tabular_model.columns.find({"id": self.column_origin_id})

    def origin_columns(self) -> set["Column"]:
        """Returns a list of columns (possibly empty) that have this column as their origin.

        Note:
            Provides the inverse information of column_origin

        """
        return self._tabular_model.columns.find_all({"column_origin_id": self.id})

    def sorting_columns(self) -> set["Column"]:
        """Returns a list of columns (possibly empty) that are sorted by this column.

        Note:
            Provides the inverse information of sort_by_column

        """
        return self._tabular_model.columns.find_all({"sort_by_column_id": self.id})

    def from_relationships(self) -> set["Relationship"]:
        return self._tabular_model.relationships.find_all({"from_column_id": self.id})

    def to_relationships(self) -> set["Relationship"]:
        return self._tabular_model.relationships.find_all({"to_column_id": self.id})

    def relationships(self) -> set["Relationship"]:
        return self.from_relationships() | self.to_relationships()

    def format_string_definition(self) -> "FormatStringDefinition | None":
        try:
            return self._tabular_model.format_string_definitions.find(lambda fsd: fsd.object() == self)
        except RowNotFoundError:
            return None

    def perspective_columns(self) -> set["PerspectiveColumn"]:
        return set(self._tabular_model.perspective_columns.find_all({"column_id": self.id}))
