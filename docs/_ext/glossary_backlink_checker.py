import dataclasses
from typing import Any

from docutils import nodes
from sphinx.addnodes import desc, desc_signature, pending_xref
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging

_logger = sphinx_logging.getLogger(__name__)


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("refcheck_ignore_documents", [], "env", list)
    collector = GlossaryRefChecker()
    # Capture pending cross-refs before resolution
    app.connect("doctree-read", collector.process_doc_read)
    app.connect("doctree-resolved", collector.check_glossary_refs)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


@dataclasses.dataclass
class MismatchedTermData:
    found_undeclared: set[str]
    declared_not_found: set[str]
    ref_col_seen: bool


class GlossaryRefChecker:
    """
    A Sphinx extension to validate glossary term references and their back-references.

    This extension ensures that all glossary terms referenced in the documentation
    are properly declared and that their "Referenced by" sections are consistent.
    It helps maintain the integrity of cross-references in the documentation,
    improving its accuracy and reliability for users.

    This validation approach allows for all references to be resolved fully before
    checking their validity without a need to modify the documents in progress, which
    would spawn further reference objects.
    """

    def process_doc_read(self, app: Sphinx, doctree: nodes.document) -> None:
        docname = app.env.docname
        if not hasattr(app.env, "glossary_term_refs"):
            app.env.glossary_term_refs = {}  # type: ignore

        for node in doctree.findall(
            lambda n: isinstance(n, (pending_xref, nodes.reference)),
        ):
            if node.get("reftype") != "term":
                continue

            term = node.get("reftarget", "")
            anchor = None

            # Check if inside an autodoc class directive
            parent = node
            while parent and not (
                isinstance(parent, desc) and parent.get("objtype") == "class"
            ):
                parent = parent.parent

            if parent:
                # It's inside a class doc
                sig_node = parent.next_node(desc_signature)
                if sig_node and sig_node.get("ids"):
                    anchor = sig_node["ids"][0]
            else:
                # fallback: use nearest parent with an ID (like a section)
                parent = node
                while parent:
                    if parent.get("ids"):
                        anchor = parent["ids"][0]
                        break
                    parent = parent.parent

            if not anchor:
                # fallback to synthetic anchor if no ID found (should be rare)
                anchor = f"auto-ref-{hash(node.astext()) % 100000}"

            _logger.verbose(
                f"[GlossaryRefCheck] Glossary term reference found: term=%r, doc=%r, anchor=%r",
                term,
                docname,
                anchor,
            )

            app.env.glossary_term_refs.setdefault(term, set()).add((docname, anchor))  # type: ignore

    def check_glossary_refs(self, app: Sphinx, doctree: nodes.document, docname: str):
        if docname != "glossary":
            return

        ignored_pages: list[str] = [
            page.lower() for page in app.config.refcheck_ignore_documents
        ]
        mismatched_terms: dict[str, MismatchedTermData] = {}

        for node in doctree.findall(nodes.definition_list_item):
            term_definitions: set[str] = set()
            for child in node.findall(nodes.term):
                child_text = child.astext()
                term_definitions.add(child_text)
                mismatched_terms[child_text] = MismatchedTermData(
                    set(),
                    set(),
                    ref_col_seen=False,
                )

            refs_map: dict[str, set[tuple[str, str]]] = getattr(
                app.env,
                "glossary_term_refs",
                {},
            )

            for ul in node.findall(nodes.bullet_list):
                if "x-ref-col" not in ul.get("classes", []):
                    continue

                listed_refs: set[str] = set()
                for ul_li in ul.findall(nodes.list_item):
                    for para in ul_li.findall(nodes.paragraph):
                        for ref in para.findall(nodes.reference):
                            refuri = ref.attributes.get("refuri")
                            listed_refs.add(str(refuri).split("#")[-1])

                combined_found_refs: set[str] = set()
                for t_def in term_definitions:
                    if (refs := refs_map.get(t_def)) is None:
                        continue
                    for referrer_doc_name, reference in refs:
                        if referrer_doc_name in ignored_pages:
                            continue

                        combined_found_refs.add(reference)

                found_but_undeclared = combined_found_refs.difference(listed_refs)
                declared_but_not_found = listed_refs.difference(combined_found_refs)
                for t_def in term_definitions:
                    mismatched_terms[t_def] = MismatchedTermData(
                        found_but_undeclared,
                        declared_but_not_found,
                        ref_col_seen=True,
                    )

        if any(
            (
                not term_data.ref_col_seen
                or len(term_data.found_undeclared) != 0
                or len(term_data.declared_not_found) != 0
            )
            for term_data in mismatched_terms.values()
        ):
            problem_terms: dict[str, MismatchedTermData] = {}
            for term, term_data in mismatched_terms.items():
                if not term_data.ref_col_seen:
                    problem_terms[term] = term_data
                    _logger.error(
                        "[GlossaryRefCheck] Could not find a 'Referenced by' "
                        "section with an 'x-ref-col' class for term %r",
                        term,
                    )
                elif (
                    len(term_data.found_undeclared) != 0
                    or len(term_data.declared_not_found) != 0
                ):
                    problem_terms[term] = term_data
                    _logger.error(
                        "[GlossaryRefCheck] 'Referenced by' section mismatch for "
                        "term %r: %r",
                        term,
                        term_data,
                    )
        else:
            if len(ignored_pages) > 0:
                _logger.info(
                    "[GlossaryRefCheck] Ignored pages: %s",
                    ", ".join(ignored_pages),
                )
            _logger.info(
                "[GlossaryRefCheck] All glossary term references back-referenced correctly!",
            )
