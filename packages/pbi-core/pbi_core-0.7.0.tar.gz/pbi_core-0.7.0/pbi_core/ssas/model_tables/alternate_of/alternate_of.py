from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasReadonlyRecord


@define()
class AlternateOf(SsasReadonlyRecord):
    """TBD.

    SSAS spec:
    """

    _discover_category: str = "TMSCHEMA_ALTERNATE_OF_DEFINITIONS"
