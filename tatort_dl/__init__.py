from queue import Queue

from tabulate import tabulate

from tatort_dl.api.episode import Episode, get_episodes
from tatort_dl.args import parser
from tatort_dl.download import Downloader
from tatort_dl.filter import apply_filters
from tatort_dl.order import apply_order


def main():
    args = parser.parse_args()
    downloader = Downloader(
        args.output_dir,
        args.tmp_dir,
        args.worker_count,
        args.concurrent_fragment_downloads,
    )
    print("Fetching information about episodes...")
    episodes = get_episodes()
    episodes_count = len(episodes)
    if args.limit:
        args.filter_not_downloaded = True
        args.filter_downloadable = True
    episodes = apply_filters(episodes, downloader, args)
    episodes = apply_order(episodes, args.order_by)
    if args.order_inverse:
        episodes.reverse()

    if args.limit:
        episodes = episodes[: args.limit]

    download = True

    if args.list_investigators:
        download = False
        investigators = set([i for e in episodes for i in e.meta.investigators])
        print(tabulate([[i] for i in list(investigators)]))

    if args.list:
        download = False
        e = [
            {
                "Nr": episode.meta.id,
                "Title": episode.meta.title,
                "Investigators": episode.meta.investigators[0],
                "Case": episode.meta.case,
                "Available to": (
                    (episode.ard.available_to.strftime("%d.%m.%Y"))
                    if episode.ard
                    else "-"
                ),
                "Downloaded": "Yes" if downloader.is_downloaded(episode) else "No",
            }
            for episode in episodes
        ]

        print(tabulate(e, headers="keys"))

    if download:
        downloader.worker_count = min(downloader.worker_count, len(episodes))
        episodes: list[Episode] = [
            e for e in episodes if e.ard and not downloader.is_downloaded(e)
        ]
        queue = Queue()
        for e in episodes:
            queue.put(e)
        print(f"Downloading {len(episodes)} episodes...")
        downloader.download(queue)
