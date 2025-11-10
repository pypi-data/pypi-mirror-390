from attrs import field
from git import TYPE_CHECKING

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

from .enums import Granularity, PolicyType, RefreshMode

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Table


@define()
class RefreshPolicy(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/e11ae511-5064-470b-8abc-e2a4dd3999e6)
    This class represents the refresh policy for a partition in a Tabular model.
    """

    incremental_granularity: Granularity = field(default=Granularity.DAY, eq=True)
    incremental_periods: int = field(default=1, eq=True)
    incremental_periods_offset: int = field(default=0, eq=True)
    mode: RefreshMode = field(default=RefreshMode.IMPORT, eq=True)
    policy_type: PolicyType = field(default=PolicyType.BASIC, eq=True)
    polling_expression: str = field(eq=True)
    rolling_window_granularity: Granularity = field(default=Granularity.DAY, eq=True)
    rolling_window_periods: int = field(default=1, eq=True)
    source_expression: str = field(eq=True)
    table_id: int = field(eq=True)

    _commands: BaseCommands = field(default=SsasCommands.refresh_policy, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_REFRESH_POLICIES"
    _db_field_names = {
        "id": "ID",
        "incremental_granularity": "IncrementalGranularity",
        "incremental_periods": "IncrementalPeriods",
        "incremental_periods_offset": "IncrementalPeriodsOffset",
        "mode": "Mode",
        "policy_type": "PolicyType",
        "polling_expression": "PollingExpression",
        "rolling_window_granularity": "RollingWindowGranularity",
        "rolling_window_periods": "RollingWindowPeriods",
        "source_expression": "SourceExpression",
        "table_id": "TableID",
    }

    def table(self) -> "Table":
        return self._tabular_model.tables.find(self.table_id)

    def parents_base(self) -> frozenset[LinkedEntity]:
        return LinkedEntity.from_iter({self.table()}, by="table")
