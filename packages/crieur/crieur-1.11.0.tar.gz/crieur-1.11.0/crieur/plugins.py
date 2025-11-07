from typing import Any, Dict, List, Match, Union

from mistune.core import BlockState

__all__ = ["inline_footnotes"]

# https://michelf.ca/projects/php-markdown/extra/#footnotes
INLINE_FOOTNOTE = r"\^\[(?P<footnote_inlined>[^\]]*)\]"


def parse_inline_footnote(
    inline: "InlineParser", m: Match[str], state: "InlineState"
) -> int:
    key = m.group("footnote_inlined")
    notes = state.env.get("inline_footnotes")
    if not notes:
        notes = []
    if key not in notes:
        notes.append(key)
        state.env["inline_footnotes"] = notes
    state.append_token(
        {
            "type": "footnote_ref",
            "raw": key,
            "attrs": {"index": notes.index(key) + 1},
        }
    )
    return m.end()


def parse_footnote_item(
    block: "BlockParser", key: str, index: int, state: BlockState
) -> Dict[str, Any]:
    return {
        "type": "footnote_item",
        "children": [{"type": "paragraph", "text": key}],
        "attrs": {"key": key, "index": index},
    }


def md_footnotes_hook(
    md: "Markdown", result: Union[str, List[Dict[str, Any]]], state: BlockState
) -> Union[str, List[Dict[str, Any]]]:
    notes = state.env.get("inline_footnotes")
    if not notes:
        return result

    children = [
        parse_footnote_item(md.block, k, i + 1, state) for i, k in enumerate(notes)
    ]
    state = BlockState()
    state.tokens = [{"type": "footnotes", "children": children}]
    output = md.render_state(state)
    return result + output  # type: ignore[operator]


def render_inline_footnote_ref(renderer: "BaseRenderer", key: str, index: int) -> str:
    i = str(index)
    html = '<sup class="footnote-ref" id="fnref-' + i + '">'
    return html + '<a href="#fn-' + i + '">' + i + "</a></sup>"


def render_inline_footnotes(renderer: "BaseRenderer", text: str) -> str:
    return '<hr><section class="footnotes">\n<ol>\n' + text + "</ol>\n</section>\n"


def render_inline_footnote_item(
    renderer: "BaseRenderer", text: str, key: str, index: int
) -> str:
    i = str(index)
    back = '<a href="#fnref-' + i + '" class="footnote">&#8617;</a>'
    text = text.rstrip()[:-4] + back + "</p>"
    return '<li id="fn-' + i + '">' + text + "</li>\n"


def inline_footnotes(md: "Markdown") -> None:
    """A mistune plugin to support inline footnotes, spec defined at
    https://michelf.ca/projects/php-markdown/extra/#footnotes

    Here is an example:

    .. code-block:: text

        That's some text with a footnote.^[And that's the footnote.]

    It will be converted into HTML:

    .. code-block:: html

        <p>That's some text with a footnote.<sup class="footnote-ref" id="fnref-1"><a href="#fn-1">1</a></sup></p>
        <section class="footnotes">
        <ol>
        <li id="fn-1"><p>And that's the footnote.<a href="#fnref-1" class="footnote">&#8617;</a></p></li>
        </ol>
        </section>

    :param md: Markdown instance
    """
    md.inline.register(
        "inline_footnote",
        INLINE_FOOTNOTE,
        parse_inline_footnote,
        before="link",
    )
    md.after_render_hooks.append(md_footnotes_hook)

    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("footnote_ref", render_inline_footnote_ref)
        md.renderer.register("footnote_item", render_inline_footnote_item)
        md.renderer.register("footnotes", render_inline_footnotes)
