from argparse import ArgumentParser
from datetime import datetime
from os import environ

parser = ArgumentParser(prog="tatort-dl", description="A downloader for Tatort movies")
parser.add_argument("-l", "--list", action="store_true")
parser.add_argument("--list-investigators", action="store_true")
parser.add_argument("-o", "--output-dir", default=environ.get("OUTPUT_DIR", "videos"))
parser.add_argument("-t", "--tmp-dir", type=str, default=environ.get("TMP_DIR", ".tmp"))
parser.add_argument("--worker-count", type=int, default=4)
parser.add_argument("-N", "--concurrent-fragment-downloads", type=int, default=4)

# filters
parser.add_argument(
    "--filter-downloaded", action="store_true", help="Filter for downloaded videos"
)
parser.add_argument(
    "--filter-not-downloaded",
    action="store_true",
    help="Filter already downloaded videos out",
)

parser.add_argument(
    "--filter-downloadable",
    action="store_true",
    help="When downloading this filter is automaticly applied",
)
parser.add_argument("--filter-investigators", action="append", default=[])
parser.add_argument(
    "--filter-access-until",
    type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    help="Filter all downloadable videos that are available until a date. The date should be in the format YYYY-MM-DD.",
)

parser.add_argument("--order-by", choices=["number", "access"], default="number")
parser.add_argument("--order-inverse", action="store_true")
parser.add_argument(
    "--limit",
    type=int,
    help="Limit the videos that should be downloaded. Videos that are already downloaded or are not downloable are filtered out.",
)
