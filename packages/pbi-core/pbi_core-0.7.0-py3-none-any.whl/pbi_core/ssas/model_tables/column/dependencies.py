from typing import TYPE_CHECKING

from .helpers import HelpersMixin

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Measure, TablePermission, Variation


class DependencyMixin(HelpersMixin):
    def child_measures(self, *, recursive: bool = False) -> set["Measure"]:
        """Returns measures dependent on this Column."""
        object_type = self._column_type()
        dependent_measures = self._tabular_model.calc_dependencies.find_all({
            "referenced_object_type": object_type,
            "referenced_table": self.table().name,
            "referenced_object": self.name(),
            "object_type": "MEASURE",
        })
        child_keys: list[tuple[str | None, str]] = [(m.table, m.object) for m in dependent_measures]
        full_dependencies = [m for m in self._tabular_model.measures if (m.table().name, m.name) in child_keys]

        if recursive:
            recursive_dependencies: set[Measure] = set()
            for dep in full_dependencies:
                if f"[{self.name()}]" in str(dep.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.child_measures(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{self.name()}]" in str(x.expression)}

    def parent_measures(self, *, recursive: bool = False) -> set["Measure"]:
        """Returns measures this column is dependent on.

        Note:
            Calculated columns can use Measures too :(.

        """
        object_type = self._column_type()
        dependent_measures = self._tabular_model.calc_dependencies.find_all({
            "object_type": object_type,
            "table": self.table().name,
            "object": self.name(),
            "referenced_object_type": "MEASURE",
        })
        parent_keys = [(m.referenced_table, m.referenced_object) for m in dependent_measures]
        full_dependencies = [m for m in self._tabular_model.measures if (m.table().name, m.name) in parent_keys]

        if recursive:
            recursive_dependencies: set[Measure] = set()
            for dep in full_dependencies:
                if f"[{dep.name}]" in str(self.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.parent_measures(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{x.name}]" in str(self.expression)}

    def child_columns(self, *, recursive: bool = False) -> set["Column"]:
        """Returns columns dependent on this Column.

        Note:
            Only occurs when the dependent column is calculated (expression is not None).

        """
        object_type = self._column_type()
        dependent_measures = self._tabular_model.calc_dependencies.find_all({
            "referenced_object_type": object_type,
            "referenced_table": self.table().name,
            "referenced_object": self.name(),
        })
        assert all(m.table is not None for m in dependent_measures)
        child_keys: list[tuple[str, str]] = [  # pyright: ignore reportAssignmentType
            (m.table, m.object) for m in dependent_measures if m.object_type in {"CALC_COLUMN", "COLUMN"}
        ]
        full_dependencies = [c for c in self._tabular_model.columns if (c.table().name, c.name()) in child_keys]

        if sorting_columns := self.sorting_columns():
            full_dependencies.extend(sorting_columns)

        if recursive:
            recursive_dependencies: set[Column] = set()
            for dep in full_dependencies:
                if f"[{self.name()}]" in str(dep.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.child_columns(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{self.name()}]" in str(x.expression)}

    def parent_columns(self, *, recursive: bool = False) -> set["Column"]:
        """Returns Columns this Column is dependent on.

        Note:
            Parent columns are non-empty only when the column is calculated.
            Columns defined by a PowerQuery import or DirectQuery do not have parent columns.

        """
        object_type = self._column_type()
        if object_type == "COLUMN":
            return set()
        dependent_measures = self._tabular_model.calc_dependencies.find_all({
            "object_type": object_type,
            "table": self.table().name,
            "object": self.name(),
        })
        parent_keys = {
            (m.referenced_table, m.referenced_object)
            for m in dependent_measures
            if m.referenced_object_type in {"CALC_COLUMN", "COLUMN"}
        }
        full_dependencies = [c for c in self._tabular_model.columns if (c.table().name, c.name()) in parent_keys]
        if sort_col := self.sort_by_column():
            full_dependencies.append(sort_col)

        if recursive:
            recursive_dependencies: set[Column] = set()
            for dep in full_dependencies:
                if f"[{dep.name()}]" in str(self.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.parent_columns(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{x.name()}]" in str(self.expression)}

    def child_table_permissions(self) -> set["TablePermission"]:
        """Returns table permissions dependent via DAX on this Column."""
        object_type = self._column_type()
        dependent_permissions = self._tabular_model.calc_dependencies.find_all({
            "referenced_object_type": object_type,
            "referenced_table": self.table().name,
            "referenced_object": self.name(),
            "object_type": "ROWS_ALLOWED",
        })

        full_dependencies: list[TablePermission] = []
        for dp in dependent_permissions:
            table, rls_name = dp.table, dp.object
            role = self._tabular_model.roles.find({"name": rls_name})
            full_dependencies.extend(
                tp
                for tp in role.table_permissions()
                if tp.table().name == table and f"[{self.name()}]" in str(tp.filter_expression)
            )

        return set(full_dependencies)

    def child_variations(self) -> set["Variation"]:
        return self._tabular_model.variations.find_all(lambda v: v.column_id == self.id)

    def child_default_variations(self) -> set["Variation"]:
        return self._tabular_model.variations.find_all(lambda v: v.default_column_id == self.id)
