import re
from dataclasses import dataclass
from datetime import datetime
from os import closerange
from pathlib import Path
from textwrap import dedent
from typing import Optional

import mistune
from citeproc import (
    Citation,
    CitationItem,
    CitationStylesBibliography,
    CitationStylesStyle,
    formatter,
)
from citeproc.source.bibtex import BibTeX
from dataclass_wizard import DatePattern, DumpMeta, YAMLWizard
from dataclass_wizard import errors as dw_errors
from PIL import Image, UnidentifiedImageError
from slugify import slugify
from yaml.composer import ComposerError

from .generator import mistune_plugins
from .typography import typographie

RE_CITATIONS_REFS = re.compile(r"\[\@(?P<ref>.*)\]")


@dataclass
class Settings:
    title: str
    base_url: str
    extra_vars: str
    target_path: Path
    source_path: Path
    statics_path: Path
    templates_path: Path
    csl_path: Path
    without_statics: bool
    feed_limit: int


class FrenchTypographyRenderer(mistune.HTMLRenderer):
    """Apply French typographic rules to text."""

    def text(self, text):
        text = text.replace("\\ ", " ")
        return typographie(super().text(text), html=True)

    def block_html(self, html):
        html = html.replace("\\ ", " ")
        return typographie(super().block_html(html), html=True)


class ImgsWithSizesRenderer(FrenchTypographyRenderer):
    """Renders images as <figure>s and add sizes."""

    def __init__(self, escape=True, allow_harmful_protocols=None, article=None):
        super().__init__(escape, allow_harmful_protocols)
        self._article = article

    def paragraph(self, text):
        # In case of a figure, we do not want the (non-standard) paragraph.
        if text.strip().startswith("<figure>"):
            return text
        return super().paragraph(text)

    def image(self, text, url, title=None):
        if self._article.images_path is None:
            print(f"Image with URL `{url}` is discarded.")
            return ""
        full_path = self._article.images_path.resolve().parent / url
        try:
            image = Image.open(full_path)
        except (IsADirectoryError, FileNotFoundError, UnidentifiedImageError):
            print(f"`{full_path}` is not a valid image.")
            return ""
        width, height = image.size
        caption = f"<figcaption>{text}</figcaption>" if text else ""
        full_url = f"{self._article.settings.base_url}{self._article.url}{url}"
        return dedent(
            f"""\
            <figure>
                <a href="{full_url}"
                    title="Cliquer pour une version haute résolution">
                    <img
                        src="{full_url}"
                        width="{width}" height="{height}"
                        loading="lazy"
                        decoding="async"
                        alt="{text}">
                </a>
                {caption}
            </figure>
            """
        )


@dataclass
class Numero(YAMLWizard):
    _id: str
    name: str
    description: str
    metadata: str
    articles: list

    def __post_init__(self):
        self.slug = slugify(self.name)

    def configure_articles(self, yaml_path, settings):
        # Preserves abstract_fr key (vs. abstract-fr) when converting to_yaml()
        DumpMeta(key_transform="SNAKE").bind_to(Article)

        loaded_articles = []
        for article in self.articles:
            article_slug = slugify(article["article"]["title"])
            article_folder = (
                yaml_path.parent / f"{article_slug}-{article['article']['_id']}"
            )
            article_yaml_path = article_folder / f"{article_slug}.yaml"
            try:
                try:
                    loaded_article = Article.from_yaml_file(article_yaml_path)
                except ComposerError:
                    loaded_article = Article.from_yaml(
                        article_yaml_path.read_text().split("---")[1]
                    )
            except dw_errors.ParseError as e:
                print(f"Metadata error in `{article['article']['title']}`:")
                print(e)
                exit(1)
            if not loaded_article.date:
                print(f"Article `{loaded_article.title}` skipped (no date).")
                continue
            if loaded_article.date > datetime.today().date():
                print(
                    f"Article `{loaded_article.title}` skipped "
                    f"(future date: {loaded_article.date})."
                )
                continue
            if not loaded_article.id:
                loaded_article.id = article_slug
            loaded_article.content_md = (
                article_folder / f"{article_slug}.md"
            ).read_text()
            loaded_article.content_bib_path = article_folder / f"{article_slug}.bib"
            loaded_article.images_path = (
                article_folder / "images"
                if (article_folder / "images").exists()
                else None
            )
            loaded_article.numero = self
            loaded_article.settings = settings
            loaded_articles.append(loaded_article)
        self.articles = sorted(loaded_articles, reverse=True)


@dataclass
class Article(YAMLWizard):
    title: str
    title_f: str
    id: str = ""
    subtitle: str = ""
    subtitle_f: str = ""
    content_md: str = ""
    content_bib_path: Path = ""
    settings: dict | None = None
    date: Optional[DatePattern["%Y/%m/%d"]] = None  # noqa: F722
    authors: list = None
    abstract: list = None
    keywords: list = None

    def __post_init__(self):
        self.slug = slugify(self.title)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other: "Article"):
        if not isinstance(other, Article):
            return NotImplemented
        return self.date < other.date

    @property
    def url(self):
        return f"numero/{self.numero.slug}/article/{self.id}/"

    @property
    def content_html(self):
        md = mistune.create_markdown(
            renderer=ImgsWithSizesRenderer(escape=False, article=self),
            plugins=mistune_plugins,
            escape=False,
        )
        html_content = md(self.content_md)

        bib_source = BibTeX(self.content_bib_path, encoding="utf-8")
        bib_style = CitationStylesStyle(self.settings.csl_path)
        bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.html)

        # Processing citations in a document needs to be done in two passes as for some
        # CSL styles, a citation can depend on the order of citations in the
        # bibliography and thus on citations following the current one.
        # For this reason, we first need to register all citations with the
        # CitationStylesBibliography.

        citations = {}

        def clean_ref(citation_ref):
            # TODO: deal with page references (for instance `[@goody_raison_1979, pp.115]`).
            return citation_ref.split(",")[0]

        for citation_ref in RE_CITATIONS_REFS.findall(html_content):
            citation_ref = clean_ref(citation_ref)
            citation = Citation([CitationItem(citation_ref)])
            bibliography.register(citation)
            citations[citation_ref] = citation

        def warn(citation_item):
            print(
                "WARNING: Reference with key '{}' not found in the bibliography.".format(
                    citation_item.key
                )
            )

        # In the second pass, CitationStylesBibliography can generate citations.
        # CitationStylesBibliography.cite() requires a callback function to be passed
        # along to be called in case a CitationItem's key is not present in the
        # bibliography.

        def replace_reference(match_object):
            citation_ref = match_object.group("ref")
            citation_ref = clean_ref(citation_ref)
            return "".join(
                f"""
                <a href="#ref_{citation_ref}" id="anchor_{citation_ref}">
                    {bibliography.cite(citations[citation_ref], warn)}
                </a>
            """.split("\n")
            )

        html_content = re.sub(RE_CITATIONS_REFS, replace_reference, html_content)
        html_bibliography = ""

        def clean_item(item):
            # As of 2025, citeproc-py does not support repeated punctuation.
            return str(item).replace("..", ".").replace(".</i>.", ".</i>")

        for citation, item in zip(bibliography.items, bibliography.bibliography()):
            citation_ref = citation.reference.get("key")
            cleaned_item = clean_item(item)
            html_bibliography += f"""
            <li>
                <span id="ref_{citation_ref}">
                    {cleaned_item}
                    <a href="#anchor_{citation_ref}">↩</a>
                </span>
            </li>
            """

        html_content = html_content.replace(
            "<h2>Bibliographie</h2>",
            f"<h2>Bibliographie</h2>\n\n<ul>{html_bibliography}</ul>",
        )

        return html_content


def configure_numero(yaml_path, settings):
    # Preserves abstract_fr key (vs. abstract-fr) when converting to_yaml()
    DumpMeta(key_transform="SNAKE").bind_to(Numero)

    try:
        numero = Numero.from_yaml_file(yaml_path)
    except ComposerError:
        numero = Numero.from_yaml(yaml_path.read_text().split("---")[1])

    numero.configure_articles(yaml_path, settings)
    return numero


@dataclass
class Keyword:
    slug: str
    name: str
    articles: list

    def __eq__(self, other):
        return self.slug == other.slug

    def __lt__(self, other: "Keyword"):
        if not isinstance(other, Keyword):
            return NotImplemented
        len_self = len(self.articles)
        len_other = len(other.articles)
        if len_self == len_other:
            return self.slug > other.slug
        return len_self < len_other


@dataclass
class Author:
    slug: str
    forname: str
    surname: str
    articles: list

    def __str__(self):
        return f"{self.forname} {self.surname}"

    def __eq__(self, other):
        return self.slug == other.slug

    def __lt__(self, other: "Author"):
        if not isinstance(other, Author):
            return NotImplemented
        len_self = len(self.articles)
        len_other = len(other.articles)
        if len_self == len_other:
            return self.slug > other.slug
        return len_self < len_other


def collect_keywords(numeros):
    keywords = {}
    for numero in numeros:
        for article in numero.articles:
            article_keywords = []
            for kwds in article.keywords:
                if kwds.get("list") and kwds.get("lang") == "fr":  # TODO: en?
                    for keyword in kwds.get("list", "").split(", "):
                        keyword_slug = slugify(keyword)
                        if keyword_slug in keywords:
                            keywords[keyword_slug].articles.append(article)
                            kw = keywords[keyword_slug]
                        else:
                            kw = Keyword(
                                slug=keyword_slug, name=keyword, articles=[article]
                            )
                            keywords[keyword_slug] = kw
                        article_keywords.append(kw)
            article.keywords = article_keywords
    return dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))


def collect_authors(numeros):
    authors = {}
    for numero in numeros:
        for article in numero.articles:
            article_authors = []
            if not article.authors:
                continue
            for athr in article.authors:
                author_forname = athr.get("forname", "")
                author_surname = athr.get("surname", "")
                author_name = f"{author_forname} {author_surname}".strip()
                if not author_name:
                    continue
                author_slug = slugify(author_name)
                if author_slug in authors:
                    authors[author_slug].articles.append(article)
                    kw = authors[author_slug]
                else:
                    kw = Author(
                        slug=author_slug,
                        forname=author_forname,
                        surname=author_surname,
                        articles=[article],
                    )
                    authors[author_slug] = kw
                article_authors.append(kw)
            article.authors = article_authors
    return dict(sorted(authors.items(), key=lambda item: item[1], reverse=True))
