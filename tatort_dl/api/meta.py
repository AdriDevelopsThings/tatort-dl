from dataclasses import dataclass
from re import S

import requests
from bs4 import BeautifulSoup, Tag

from tatort_dl.cache import cache

WIKIPEDIA_URL = "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen"
WIKIPEDIA_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"


@dataclass
class Meta:
    id: int
    title: str
    investigators: list[str]
    case: int
    published: str


def _get_wikipedia_html() -> str:
    cache_key = {"ctx": "wikipedia"}
    cached = cache.get(cache_key)
    if cached:
        return cached

    response = requests.get(WIKIPEDIA_URL, headers={"User-Agent": WIKIPEDIA_USER_AGENT})
    response.raise_for_status()
    if "text/html" not in response.headers.get("Content-Type", ""):
        raise ValueError("Request to wikipedia didn't return html")
    content = response.text
    cache.set(cache_key, content, 3600)
    return content


def _get_wikipedia_table_head_body() -> tuple[Tag, list[Tag]]:
    soup = BeautifulSoup(_get_wikipedia_html(), features="html.parser")
    content = soup.select_one("div#bodyContent")
    assert content
    table = content.select_one("table")
    assert table

    head = table.select_one("tr")
    assert head
    body = table.select("tr")[1:]

    return (head, body)


def _wikipedia_tr_to_meta(header: list[str], tr: Tag) -> Meta:
    tds = tr.select("td")

    id_s = tds[header.index("Folge")].get_text(strip=True)
    id = int(id_s)

    title_tag = tds[header.index("Titel")].select_one("a")
    assert title_tag
    title = title_tag.text

    investigators: list[str] = []
    investigator_tags = tds[header.index("Ermittler")].select("a")
    for t in investigator_tags:
        investigators.append(t.text)

    case_s = tds[header.index("Fall")].get_text(strip=True)
    case_s = case_s.split(" ")[0]
    case = int(case_s)

    published = tds[header.index("Erstausstrahlung")].get_text(strip=True)

    return Meta(
        id=id, title=title, investigators=investigators, case=case, published=published
    )


def get_episodes_meta() -> list[Meta]:
    (head, body) = _get_wikipedia_table_head_body()

    header: list[str] = [h.get_text(strip=True) for h in head.select("th")]
    metas: list[Meta] = [_wikipedia_tr_to_meta(header, tr) for tr in body]

    return metas
