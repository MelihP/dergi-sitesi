import nh3
from bs4 import BeautifulSoup
from django.template.defaultfilters import linebreaks
from django.utils.safestring import mark_safe


def clean_html(value):
    return nh3.clean(
        value or "",
        tags={
            "p",
            "br",
            "h2",
            "h3",
            "strong",
            "b",
            "em",
            "i",
            "u",
            "s",
            "blockquote",
            "ol",
            "ul",
            "li",
            "a",
        },
        attributes={
            "a": {"href", "title"},
        },
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )


def plain_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.find_all(
        ["p", "h2", "h3", "li", "blockquote", "br"]
    ):
        element.insert_after("\n")

    return soup.get_text().strip()


def render_content(article):
    if article.content_html:
        html = clean_html(article.content_html)
    else:
        html = linebreaks(
            article.content,
            autoescape=True,
        )
        html = clean_html(html)

    # Pasted documents may use non-breaking spaces between every word.
    # Normalize text nodes only, preserving markup and link attributes.
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all(string=True):
        normalized = str(node).replace("\u00a0", " ").replace("\u202f", " ")
        if normalized != str(node):
            node.replace_with(normalized)

    return mark_safe(str(soup))