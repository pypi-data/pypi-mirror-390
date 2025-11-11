from docutils import nodes
from sphinx.writers.html import HTMLTranslator
from html import escape


class CustomHTMLTranslator(HTMLTranslator):
    def visit_title(self, node) -> None:
        """Overrides the default title visitor.

        This method checks if a title is inside an admonition. If it is,
        it wraps the title text in a `<span>` tag to allow for custom
        styling, and then prevents further processing of the node.
        For all other titles, it calls the original `visit_title` method
        to ensure default rendering.
        """
        if isinstance(node.parent, nodes.Admonition):
            self.body.append(f"<span>{escape(node.astext())}</span>")
            raise nodes.SkipNode
        else:
            super().visit_title(node)
