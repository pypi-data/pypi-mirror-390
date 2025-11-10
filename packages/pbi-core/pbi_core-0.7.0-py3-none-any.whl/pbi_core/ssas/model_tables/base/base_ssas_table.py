from attrs import field
from bs4 import BeautifulSoup
from structlog import get_logger

from pbi_core.attrs import define
from pbi_core.ssas.model_tables._group import IdBase
from pbi_core.ssas.server import DISCOVER_TEMPLATE

from .helpers import HelperMixin
from .lineage import LineageMixin
from .ssas import SsasMixin
from .tabular import TabularMixin

logger = get_logger()


@define()
class SsasTable(IdBase, TabularMixin, HelperMixin, SsasMixin, LineageMixin):
    _discover_category: str = field(default="NOT_SET")

    def discover(self) -> BeautifulSoup:
        xml_command = DISCOVER_TEMPLATE.render(
            db_name=self._tabular_model.db_name,
            discover_entity=self._discover_category,
        )
        return self._tabular_model.server.query_xml(xml_command, db_name=self._tabular_model.db_name)
