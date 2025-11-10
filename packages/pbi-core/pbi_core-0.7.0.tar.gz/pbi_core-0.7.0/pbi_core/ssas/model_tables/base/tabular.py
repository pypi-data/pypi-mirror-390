from attrs import field
from bs4 import BeautifulSoup
from git import TYPE_CHECKING
from structlog import get_logger

from pbi_core.attrs import define
from pbi_core.ssas.server import BaseTabularModel

logger = get_logger()

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.annotation import Annotation


@define()
class TabularMixin:
    _tabular_model: BaseTabularModel = field(repr=False, eq=False, init=False)

    def query_dax(self, query: str, db_name: str | None = None) -> None:
        """Helper function to remove the ``._tabular_model.server`` required to run a DAX query from an SSAS element."""
        logger.debug("Executing DAX query", query=query, db_name=db_name)
        self._tabular_model.server.query_dax(query, db_name=db_name)

    def query_xml(self, query: str, db_name: str | None = None) -> BeautifulSoup:
        """Helper function to remove the ``._tabular_model.server`` required to run an XML query in SSAS."""
        logger.debug("Executing XML query", query=query, db_name=db_name)
        return self._tabular_model.server.query_xml(query, db_name)

    def annotations(self) -> set["Annotation"]:
        """Get associated dependent annotations.

        Returns:
            (set[Annotation]): A list of the annotations linked to this object

        """
        # Althought annotations are not children of every concrete SsasTable, they are
        # of enough to warrant inclusion here.
        return self._tabular_model.annotations.find_all(lambda a: a.object() == self)
