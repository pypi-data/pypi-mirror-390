from typing import TYPE_CHECKING, Literal

from .enums import ColumnType
from .relationships import RelationshipMixin

if TYPE_CHECKING:
    from pbi_parsers import dax


class HelpersMixin(RelationshipMixin):
    def expression_ast(self) -> "dax.Expression | None":
        from pbi_parsers import dax  # noqa: PLC0415

        if not isinstance(self.expression, str):
            return None
        return dax.to_ast(self.expression)

    def is_system_table(self) -> bool:
        return bool(self.system_flags >> 1 % 2)

    def is_from_calculated_table(self) -> bool:
        return bool(self.system_flags % 2)

    def is_calculated_column(self) -> bool:
        return self.type == ColumnType.CALCULATED

    def is_normal(self) -> bool:
        """Returns True if the column is not a row number column or attached to a system/private table."""
        if self.type == ColumnType.ROW_NUMBER:
            return False
        if self.table().is_private:
            return False
        return not self.is_system_table()

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.name()

    def _column_type(self) -> Literal["COLUMN", "CALC_COLUMN"]:
        if self.type == ColumnType.DATA:
            return "COLUMN"
        return "CALC_COLUMN"

    def name(self) -> str:
        """Returns the name of the column.

        Note:
            It appears that [{explicit_name} {inferred_name}] can also be valid in DAX

        """
        ret = self.explicit_name if self.explicit_name is not None else self.inferred_name
        assert ret is not None, "Column must have either an explicit or inferred name"
        return ret

    def full_name(self) -> str:
        """Returns the fully qualified name for DAX queries.

        Examples:
            'TableName'[ColumnName]

        """
        table_name = self.table().name
        return f"'{table_name}'[{self.name()}]"

    def data(self, head: int = 100) -> list[int | float | str]:
        table_name = self.table().name
        ret = self._tabular_model.server.query_dax(
            f"EVALUATE TOPN({head}, SELECTCOLUMNS(ALL('{table_name}'), {self.full_name()}))",
            db_name=self._tabular_model.db_name,
        )
        return [next(iter(row.values())) for row in ret]
