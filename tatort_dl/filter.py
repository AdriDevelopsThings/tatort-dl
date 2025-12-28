from argparse import Namespace

from tatort_dl.api.episode import Episode
from tatort_dl.download import Downloader


def apply_filters(
    episodes: list[Episode], downloader: Downloader, args: Namespace
) -> list[Episode]:
    filter_investigators = set(args.filter_investigators)

    episodes = [
        episode
        for episode in episodes
        if (not args.filter_downloaded or downloader.is_downloaded(episode))
        and (not args.filter_downloadable or episode.ard)
        and (
            not args.filter_investigators
            or (set(episode.meta.investigators) & filter_investigators)
        )
        and (
            not args.filter_access_until
            or (
                episode.ard
                and (
                    episode.ard.available_to is None
                    or episode.ard.available_to.replace(tzinfo=None)
                    <= args.filter_access_until
                )
            )
        )
    ]

    return episodes
