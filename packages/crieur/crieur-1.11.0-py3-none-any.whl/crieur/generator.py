import json
import locale
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import mistune
from feedgen.feed import FeedGenerator
from jinja2 import Environment as Env
from jinja2 import FileSystemLoader
from slugify import slugify

from . import VERSION
from .typography import typographie
from .utils import neighborhood

locale.setlocale(locale.LC_ALL, "")
mistune_plugins = [
    "footnotes",
    "superscript",
    "table",
    "crieur.plugins.inline_footnotes",
]
md = mistune.create_markdown(plugins=mistune_plugins, escape=False)


def slugify_(value):
    return slugify(value)


def markdown(value):
    return md(value) if value else ""


def typography(value):
    value = value.replace("\\ ", " ")
    return typographie(value) if value else ""


def generate_html(numeros, keywords, authors, settings):
    environment = Env(
        loader=FileSystemLoader(
            [str(settings.templates_path), str(Path(__file__).parent / "templates")]
        )
    )
    environment.filters["slugify"] = slugify_
    environment.filters["markdown"] = markdown
    environment.filters["typography"] = typography

    extra_vars = json.loads(settings.extra_vars) if settings.extra_vars else {}

    common_params = {
        "title": settings.title,
        "base_url": settings.base_url,
        "numeros": numeros,
        "keywords": keywords,
        "authors": authors,
        "crieur_version": VERSION,
        **extra_vars,
    }

    template_homepage = environment.get_template("homepage.html")
    content = template_homepage.render(**common_params)
    settings.target_path.mkdir(parents=True, exist_ok=True)
    (settings.target_path / "index.html").write_text(content)

    for numero in numeros:
        template_numero = environment.get_template("numero.html")
        content = template_numero.render(numero=numero, **common_params)
        numero_folder = settings.target_path / "numero" / numero.slug
        numero_folder.mkdir(parents=True, exist_ok=True)
        (numero_folder / "index.html").write_text(content)

        template_article = environment.get_template("article.html")
        for index, previous, article, next_ in neighborhood(numero.articles):
            content = template_article.render(
                article=article,
                numero=numero,
                previous_situation=previous,
                next_situation=next_,
                **common_params,
            )
            article_folder = numero_folder / "article" / article.id
            article_folder.mkdir(parents=True, exist_ok=True)
            (article_folder / "index.html").write_text(content)
            if article.images_path:
                shutil.copytree(
                    article.images_path, article_folder / "images", dirs_exist_ok=True
                )

    for slug, keyword in keywords.items():
        template_keyword = environment.get_template("keyword.html")
        content = template_keyword.render(keyword=keyword, **common_params)
        keyword_folder = settings.target_path / "mot-clef" / keyword.slug
        keyword_folder.mkdir(parents=True, exist_ok=True)
        (keyword_folder / "index.html").write_text(content)

    for slug, author in authors.items():
        template_author = environment.get_template("author.html")
        content = template_author.render(author=author, **common_params)
        author_folder = settings.target_path / "auteur" / author.slug
        author_folder.mkdir(parents=True, exist_ok=True)
        (author_folder / "index.html").write_text(content)


def generate_feed(numeros, settings, lang="fr"):
    feed = FeedGenerator()
    feed.id(settings.base_url)
    feed.title(settings.title)
    feed.link(href=settings.base_url, rel="alternate")
    feed.link(href=f"{settings.base_url}feed.xml", rel="self")
    feed.language(lang)

    articles = sorted(
        [article for numero in numeros for article in numero.articles], reverse=True
    )

    for article in articles[: settings.feed_limit]:
        feed_entry = feed.add_entry(order="append")
        feed_entry.id(f"{settings.base_url}{article.url}")
        feed_entry.title(article.title_f)
        feed_entry.link(href=f"{settings.base_url}{article.url}")
        feed_entry.updated(
            datetime.combine(
                article.date,
                datetime.min.time(),
                tzinfo=timezone(timedelta(hours=-4), "ET"),
            )
        )
        for author in article.authors:
            feed_entry.author(name=str(author))
        feed_entry.summary(summary=article.content_html, type="html")
        if article.keywords:
            for keyword in article.keywords:
                feed_entry.category(term=keyword.name)

    feed.atom_file(settings.target_path / "feed.xml", pretty=True)
    print(f"Generated meta-feed with {settings.feed_limit} items.")
