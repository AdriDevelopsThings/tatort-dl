# tatort-dl
A downloader for Tatort videos from ARD Mediathek.

## Installation
Install this using `pipx`:
```
git clone https://github.com/adridevelopsthings/tatort-dl
pipx install .
```

## Running
First think about which videos should be downloaded and then configure the filters. Use `-l` as an option to show which videos are filtered.
```
usage: tatort-dl [-h] [-l] [--list-investigators] [-o OUTPUT_DIR] [--filter-downloaded] [--filter-not-downloaded] [--filter-downloadable]
                 [--filter-investigators FILTER_INVESTIGATORS] [--filter-access-until FILTER_ACCESS_UNTIL] [--order-by {number,access}] [--order-inverse]
                 [--limit LIMIT]

A downloader for Tatort movies

options:
  -h, --help            show this help message and exit
  -l, --list
  --list-investigators
  -o, --output-dir OUTPUT_DIR
  --filter-downloaded   Filter for downloaded videos
  --filter-not-downloaded
                        Filter already downloaded videos out
  --filter-downloadable
                        When downloading this filter is automaticly applied
  --filter-investigators FILTER_INVESTIGATORS
  --filter-access-until FILTER_ACCESS_UNTIL
                        Filter all downloadable videos that are available until a date. The date should be in the format YYYY-MM-DD.
  --order-by {number,access}
  --order-inverse
  --limit LIMIT         Limit the videos that should be downloaded. Videos that are already downloaded or are not downloable are filtered out.
  ```