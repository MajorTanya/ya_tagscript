from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import class_option
from sphinx.application import Sphinx


def setup(app: Sphinx):
    app.add_directive("styled-list", StyledList)


class StyledList(Directive):
    has_content = True
    option_spec = {
        "class": class_option,
    }

    def run(self) -> list[nodes.Node]:
        node = nodes.Element()
        self.state.nested_parse(self.content, self.content_offset, node)

        list_node = next(
            (
                child
                for child in node
                if isinstance(child, (nodes.bullet_list, nodes.enumerated_list))
            ),
            None,
        )
        if list_node is None:
            error = self.state_machine.reporter.error(
                "Expected a bullet list or enumerated list in 'styled-list' content.",
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno,
            )
            return [error]

        list_node["classes"] += self.options.get("class", [])
        return [list_node]
