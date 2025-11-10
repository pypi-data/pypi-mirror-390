from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base.base_ssas_table import SsasTable


@define()
class GroupByColumn(SsasTable):
    """TBD.

    SSAS spec:
    """

    _discover_category: str = "TMSCHEMA_GROUP_BY_COLUMNS"
    _db_field_names = {}
