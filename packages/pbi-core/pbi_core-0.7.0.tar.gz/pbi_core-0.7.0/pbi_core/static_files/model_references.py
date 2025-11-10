from typing import TYPE_CHECKING

from pbi_core.attrs import BaseValidation, define

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Column, Level, Measure, Table
    from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel


@define(repr=True)
class ModelLevelReference(BaseValidation):
    hierarchy: str
    table: str
    level: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Level":
        def level_matcher(level: "Level") -> bool:
            # TODO: I'm convinced there's different structure for normal and variation (the auto-date) hierarchies
            if level.name != self.level:
                return False
            h = level.hierarchy()
            variations = h.variations()
            if not variations:
                return (h.name == self.hierarchy) and (h.table().name == self.table)
            for v in variations:
                # This generally happens for the automatic date hierarchy.
                variation_column = v.column()
                if (
                    variation_column
                    and (variation_column.name() == self.hierarchy)
                    and (variation_column.table().name == self.table)
                ):
                    return True
            return False

        return tabular_model.levels.find(level_matcher)


@define(repr=True)
class ModelColumnReference(BaseValidation):
    column: str
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Column":
        return tabular_model.columns.find(
            lambda c: (c.name() == self.column) and (c.table().name == self.table),
        )


@define(repr=True)
class ModelTableReference(BaseValidation):
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Table":
        return tabular_model.tables.find(lambda t: (t.name == self.table))


@define(repr=True)
class ModelMeasureReference(BaseValidation):
    measure: str
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Measure":
        return tabular_model.measures.find(lambda m: (m.name == self.measure) and (m.table().name == self.table))


ModelReference = ModelColumnReference | ModelLevelReference | ModelMeasureReference
