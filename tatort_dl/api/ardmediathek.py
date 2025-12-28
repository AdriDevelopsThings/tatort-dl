from datetime import datetime
from typing import Optional

import requests
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass

from tatort_dl.cache import cache

BASE_URL = "https://api.ardmediathek.de"
WIDGET_PATH = "/page-gateway/widgets/ard/compilation"
WIDGET_ID = "71IpTwcl8yta2O3eVCSJR0"
PAGE_SIZE = 96

VIDEO_PATH = "https://www.ardmediathek.de/video"

FILTER_TITLE = ["klare Sprache"]


class PublicationService(BaseModel):
    partner: str


class Show(BaseModel):
    title: str


class Teaser(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    available_to: Optional[datetime]
    long_title: str
    id: str

    show: Show
    publication_service: PublicationService


class Pagination(BaseModel):
    total_elements: int = Field(alias="totalElements")


class Page(BaseModel):
    pagination: Pagination
    teasers: list[Teaser]


def _format_name(name: str) -> str:
    name = name.lower()
    name = name.replace("(", " ").replace(")", " ").replace("|", " ").replace(":", " ")
    words = name.split(" ")
    words = [word for word in words if word]
    name = "-".join(words)
    return name


@dataclass
class ArdEpisode:
    id: str
    title: str
    show_title: str
    partner: str
    available_to: datetime

    __download_url: Optional[str] = None

    @property
    def download_url(self) -> str:
        if self.__download_url:
            return self.__download_url

        url = f"{VIDEO_PATH}/{_format_name(self.show_title)}/{_format_name(self.title)}/{self.partner}/{self.id}"
        response = requests.head(url)
        if response.status_code == 404:
            raise RuntimeError(
                f"Download url for episode '{self.title}' ({self.id}) should be '{url}' but this page does not exist."
            )

        self.__download_url = url
        return self.__download_url


def _request_page(page: int) -> Page:
    cache_key = {"ctx": "ardmediathek_page", "page": page}
    cached = cache.get(cache_key)
    if cached:
        return Page(**cached)
    response = requests.get(
        f"{BASE_URL}{WIDGET_PATH}/{WIDGET_ID}",
        params={"pageNumber": page, "pageSize": PAGE_SIZE},
    )
    response.raise_for_status()
    j = response.json()
    cache.set(cache_key, j, 3600)
    return Page(**j)


def _episode_filter(episode: ArdEpisode) -> bool:
    for w in FILTER_TITLE:
        if w.lower() in episode.title.lower():
            return False

    return True


def get_episodes() -> list[ArdEpisode]:
    page_num = 0
    episodes: list[ArdEpisode] = []

    while True:
        page = _request_page(page_num)
        page_num += 1
        if not page.teasers:
            break

        for teaser in page.teasers:
            if not teaser.available_to:
                continue
            episode = ArdEpisode(
                id=teaser.id,
                title=teaser.long_title,
                available_to=teaser.available_to,
                show_title=teaser.show.title,
                partner=teaser.publication_service.partner,
            )

            if not _episode_filter(episode):
                continue

            episodes.append(episode)

        if len(episodes) >= page.pagination.total_elements:
            break

    return list({e.id: e for e in episodes}.values())
