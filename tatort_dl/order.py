from typing import Any

from tatort_dl.api.episode import Episode


def _order_key(episode: Episode, order: str) -> Any:
    if order == "number":
        return episode.meta.id

    if order == "access":
        assert episode.ard
        return episode.ard.available_to

    raise RuntimeError(f"Invalid order {order}")


def apply_order(episodes: list[Episode], order: str) -> list[Episode]:
    if order == "access":
        episodes = [e for e in episodes if e.ard]

    episodes.sort(key=lambda e: _order_key(e, order))
    return episodes
