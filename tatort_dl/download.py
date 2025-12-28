from os import mkdir
from os.path import exists, join
from pathlib import Path

import yt_dlp

from tatort_dl.api.episode import Episode


class Downloader:
    def __init__(self, dir: str):
        if not exists(dir):
            mkdir(dir)
        self.__dir = dir

    def __get_path(self, episode: Episode) -> str:
        filename = f"{episode.meta.case}-{episode.meta.id}-{episode.meta.title}-{episode.meta.published}.mp4"
        return join(self.__dir, episode.meta.investigators[0], filename)

    def is_downloaded(self, episode: Episode) -> bool:
        return exists(self.__get_path(episode))

    def download(self, episode: Episode):
        assert episode.ard is not None

        if self.is_downloaded(episode):
            return
        path = self.__get_path(episode)
        parent = Path(path).parent.absolute()
        if not exists(parent):
            mkdir(parent)

        params = {"outtmpl": path, "concurrent_fragment_downloads": 4}
        with yt_dlp.YoutubeDL(params) as ydl:
            ydl.download(episode.ard.download_url)
