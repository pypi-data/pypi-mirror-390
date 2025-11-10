from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasTable


@define()
class Set(SsasTable):
    """TBD.

    SSAS spec:
    """

    _discover_category: str = "TMSCHEMA_SETS"
    _db_field_names = {}
