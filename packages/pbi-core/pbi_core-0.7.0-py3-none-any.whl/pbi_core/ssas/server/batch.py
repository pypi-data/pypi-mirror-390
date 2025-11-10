import textwrap
from collections.abc import Iterable

from attrs import field

from pbi_core.attrs import define
from pbi_core.logging import get_logger
from pbi_core.ssas.server._commands import BATCH_TEMPLATE, CommandData

logger = get_logger()


@define(kw_only=False)
class Batch:
    commands: Iterable[CommandData] = field(factory=list)

    def render_xml(self) -> str:
        command_entities: dict[str, dict[str, list[CommandData]]] = {}
        for cmd in self.commands:
            command_entities.setdefault(cmd.action, {}).setdefault(cmd.entity, []).append(cmd)

        logger_info = {
            action: {entity: len(cmds) for entity, cmds in entities.items()}
            for action, entities in command_entities.items()
        }
        logger.info("Preparing Batch Command for SSAS", **logger_info)
        actions = []
        for action_data in command_entities.values():
            entity_xmls = []

            # action_cmd is just to get the type checking happy
            action_cmd = None
            for cmd_data in action_data.values():
                action_cmd = cmd_data[0]

                entities = textwrap.indent("\n".join([x._get_row_xml(x.data) for x in cmd_data]), " " * 2)
                entity_xml = action_cmd.entity_template.render(rows=entities)
                entity_xmls.append(entity_xml)

            assert action_cmd is not None

            entity_info = textwrap.indent("\n".join(entity_xmls), " " * 2)
            action_xml = action_cmd.action_template.render(
                db_name=action_cmd.db_name,
                entity_def=entity_info,
            )
            actions.append(action_xml)
        action_info = textwrap.indent("\n".join(actions), " " * 2)
        return BATCH_TEMPLATE.render(actions=action_info)
