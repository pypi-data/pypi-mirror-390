from typing import Any

import attrs
import bs4
import jinja2

from .utils import python_to_xml

BATCH_TEMPLATE = jinja2.Template(
    """
<Batch Transaction="false" xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
{{actions}}
</Batch>
""".lstrip(),
)

ROW_TEMPLATE = jinja2.Template(
    """
<row xmlns="urn:schemas-microsoft-com:xml-analysis:rowset">
{%- for k, v in fields %}
  <{{k}}>{{v}}</{{k}}>
{%- endfor %}
</row>
""".lstrip(),
)

BASE_ALTER_TEMPLATE = jinja2.Template(
    """
<Alter xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
{{entity_def}}
</Alter>
""".lstrip(),
)

# note that Transaction = true. I think it's necessary, not very tested tbqh
BASE_REFRESH_TEMPLATE = jinja2.Template(
    """
<Refresh xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
  {{entity_def}}
</Refresh>
""".lstrip(),
)
BASE_RENAME_TEMPLATE = jinja2.Template(
    """
<Alter xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
</Alter>
<Rename xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
{{entity_def}}
</Rename>
""".lstrip(),
)
BASE_DELETE_TEMPLATE = jinja2.Template(
    """
<Delete xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
{{entity_def}}
</Delete>
""".lstrip(),
)
BASE_CREATE_TEMPLATE = jinja2.Template(
    """
<Create xmlns="http://schemas.microsoft.com/analysisservices/2014/engine">
  <DatabaseID>{{db_name}}</DatabaseID>
{{entity_def}}
</Create>
""".lstrip(),
)
DISCOVER_TEMPLATE = jinja2.Template(
    """
<Batch Transaction="false" xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
  <Discover xmlns="urn:schemas-microsoft-com:xml-analysis">
    <RequestType>{{discover_entity}}</RequestType>
    <Restrictions>
      <RestrictionList>
        <DatabaseName>{{db_name}}</DatabaseName>
{{filter_expr}}
      </RestrictionList>
    </Restrictions>
    <Properties>
      <PropertyList/>
    </Properties>
  </Discover>
</Batch>
""".lstrip(),
)
base_commands = {
    "alter": BASE_ALTER_TEMPLATE,
    "create": BASE_CREATE_TEMPLATE,
    "delete": BASE_DELETE_TEMPLATE,
    "refresh": BASE_REFRESH_TEMPLATE,
    "rename": BASE_RENAME_TEMPLATE,
}


@attrs.define()
class Command:
    entity_template: jinja2.Template
    action_template: jinja2.Template
    field_order: list[str]
    action: str
    entity: str

    def sort(self, fields: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return sorted(fields, key=lambda k: self.field_order.index(k[0]))

    def to_data(self, data: dict[str, Any], db_name: str) -> "CommandData":
        return CommandData(
            entity_template=self.entity_template,
            action_template=self.action_template,
            field_order=self.field_order,
            action=self.action,
            entity=self.entity,
            data=data,
            db_name=db_name,
        )


@attrs.define()
class CommandData(Command):
    data: dict[str, str | int | bool | None]
    db_name: str

    def _get_row_xml(self, values: dict[str, Any]) -> str:
        fields: list[tuple[str, str]] = []
        for field_name, field_value in values.items():
            if field_name not in self.field_order:
                continue
            if field_value is None:
                continue
            fields.append((field_name, python_to_xml(field_value)))
        fields = self.sort(fields)
        return ROW_TEMPLATE.render(fields=fields)


class NoCommands:
    def __init__(self, entity: str, **kwargs: str) -> None:
        for field_name, template_text in kwargs.items():
            v = Command(
                entity_template=jinja2.Template(template_text),
                action_template=base_commands[field_name],
                field_order=self.get_field_order(template_text),
                action=field_name,
                entity=entity,
            )
            self.__setattr__(field_name, v)

    @staticmethod
    def get_field_order(text: str) -> list[str]:
        """Gets the order of the fields for the command, based on the ``xs:sequence`` section of the XML command."""
        tree = bs4.BeautifulSoup(text, "xml")
        row = tree.find("xs:complexType", {"name": "row"})
        assert isinstance(row, bs4.element.Tag)
        ret: list[str] = []
        for e in row.find_all("xs:element"):
            assert isinstance(e, bs4.element.Tag)
            val = e["name"]
            assert isinstance(val, str)
            ret.append(val)
        return ret


class BaseCommands(NoCommands):
    alter: Command
    create: Command
    delete: Command

    def __repr__(self) -> str:
        return "BaseCommands(alter, create, delete)"

    @staticmethod
    def new(entity: str, data: dict[str, str]) -> "BaseCommands":
        return BaseCommands(
            alter=data["alter.xml"],
            create=data["create.xml"],
            delete=data["delete.xml"],
            entity=entity,
        )


class RenameCommands(BaseCommands):
    rename: Command

    def __repr__(self) -> str:
        return "RenameCommands(alter, create, delete, rename)"

    @staticmethod
    def new(entity: str, data: dict[str, str]) -> "RenameCommands":
        return RenameCommands(
            alter=data["alter.xml"],
            create=data["create.xml"],
            delete=data["delete.xml"],
            rename=data["rename.xml"],
            entity=entity,
        )


class RefreshCommands(RenameCommands):
    refresh: Command

    def __repr__(self) -> str:
        return "RefreshCommands(alter, create, delete, rename, refresh)"

    @staticmethod
    def new(entity: str, data: dict[str, str]) -> "RefreshCommands":
        return RefreshCommands(
            alter=data["alter.xml"],
            create=data["create.xml"],
            delete=data["delete.xml"],
            rename=data["rename.xml"],
            refresh=data["refresh.xml"],
            entity=entity,
        )


class ModelCommands(NoCommands):
    alter: Command
    refresh: Command
    rename: Command

    def __repr__(self) -> str:
        return "ModelCommands(alter, refresh, rename)"

    @staticmethod
    def new(entity: str, data: dict[str, str]) -> "ModelCommands":
        return ModelCommands(
            alter=data["alter.xml"],
            refresh=data["refresh.xml"],
            rename=data["rename.xml"],
            entity=entity,
        )


Commands = BaseCommands | RenameCommands | RefreshCommands | ModelCommands
