import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Measure


@define()
class KPI(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/1289ceca-8113-4019-8f90-8132a91117cf)
    """

    description: str | None = field(default=None, eq=True)
    measure_id: int = field(eq=True)
    status_description: str | None = field(default=None, eq=True)
    status_expression: str | None = field(default=None, eq=True)
    status_graphic: str | None = field(default=None, eq=True)
    target_description: str | None = field(default=None, eq=True)
    target_expression: str | None = field(default=None, eq=True)
    target_format_string: str | None = field(default=None, eq=True)
    trend_description: str | None = field(default=None, eq=True)
    trend_expression: str | None = field(default=None, eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: BaseCommands = field(default=SsasCommands.kpi, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_KPIS"
    _db_field_names = {
        "id": "ID",
        "description": "Description",
        "measure_id": "MeasureID",
        "status_description": "StatusDescription",
        "status_expression": "StatusExpression",
        "status_graphic": "StatusGraphic",
        "target_description": "TargetDescription",
        "target_expression": "TargetExpression",
        "target_format_string": "TargetFormatString",
        "trend_description": "TrendDescription",
        "trend_expression": "TrendExpression",
        "modified_time": "ModifiedTime",
    }

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.measure().pbi_core_name()

    def measure(self) -> "Measure":
        return self._tabular_model.measures.find({"id": self.measure_id})

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.measure()}, by="measure")
