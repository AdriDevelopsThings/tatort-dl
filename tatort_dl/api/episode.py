import string
import unicodedata
from re import match, search
from typing import Optional

from pydantic.dataclasses import dataclass

from tatort_dl.api import ardmediathek, meta


@dataclass
class Episode:
    meta: meta.Meta
    ard: Optional[ardmediathek.ArdEpisode]


def _normalize_title(s: str) -> str:
    s = s.lower()
    while "(" in s and ")" in s:
        b = s.index("(")
        e = s.index(")", b)
        s = s[:b] + s[e + 1 :]

    s = s.removeprefix("tatort:")

    normalized = unicodedata.normalize("NFKD", s)
    return "".join(c for c in normalized if c in string.ascii_letters or c in ("-",))


def _meta_find_ard(
    ard: list[ardmediathek.ArdEpisode], m: meta.Meta
) -> Optional[ardmediathek.ArdEpisode]:
    for a in ard:
        a_title = _normalize_title(a.title)
        m_title = _normalize_title(m.title)

        if a_title == m_title:
            return a

        part_m = search(r"Teil (\d)", m.title)
        if not part_m:
            continue
        part_a = search(r"\((\d)\/\d\)", a.title)
        if not part_a:
            continue
        if part_m.group(1) == part_a.group(1):
            m_title = _normalize_title(m.title.replace(f"Teil {part_m.group(1)}", ""))
            if a_title == m_title:
                return a


def get_episodes() -> list[Episode]:
    ard_episodes = ardmediathek.get_episodes()
    meta_episodes = meta.get_episodes_meta()

    episodes: list[Episode] = []

    for m in meta_episodes:
        episodes.append(Episode(meta=m, ard=_meta_find_ard(ard_episodes, m)))

    return episodes
