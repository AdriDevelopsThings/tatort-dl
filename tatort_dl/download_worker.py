from os import mkdir
from os.path import basename, dirname, exists, join
from queue import Empty, Queue
from shutil import move
from threading import Thread
from traceback import format_exc
from typing import TYPE_CHECKING, Literal, Optional

import yt_dlp

from tatort_dl.api.episode import Episode
from tatort_dl.utils import ErrorLogger

if TYPE_CHECKING:
    from tatort_dl.download import Downloader


class DownloadWorker(Thread):
    def __init__(self, downloader: "Downloader", queue: Queue[Episode]) -> None:
        super().__init__()
        self.current_episode: Optional[Episode] = None
        self.status: Literal[
            "starting", "downloading", "error", "finishing", "moving", "exited"
        ] = "starting"
        self.info_dict: Optional[dict] = None
        self.error: Optional[Exception] = None
        self.stacktrace: Optional[str] = None

        self.__downloader = downloader
        self.__queue = queue

    def __yt_dlp_hook(self, d):
        self.info_dict = d
        if (
            d["status"] == "downloading"
            and "fragment_index" in d
            and d["fragment_index"] == d["fragment_count"]
        ):
            self.status = "finishing"
            return
        if d["status"] in ["downloading", "error"]:
            self.status = d["status"]
        elif d["status"] == "finished":
            self.status = "finishing"

    def run(self) -> None:
        while self.__downloader.running and not self.__queue.empty():
            try:
                episode: Episode = self.__queue.get(block=False)
            except Empty:
                break
            self.current_episode = episode
            self.status = "downloading"
            self.info_dict = None

            assert episode.ard is not None

            if self.__downloader.is_downloaded(episode):
                continue

            target_path = self.__downloader.get_episode_path(episode)
            tmp_path = join(self.__downloader.tmp, basename(target_path))

            params = {
                "outtmpl": tmp_path,
                "concurrent_fragment_downloads": self.__downloader.concurrent_fragment_downloads,
                "logger": ErrorLogger(),
                "progress_hooks": [self.__yt_dlp_hook],
            }
            try:
                with yt_dlp.YoutubeDL(params) as ydl:
                    ydl.download(episode.ard.download_url)
            except Exception as e:
                self.error = e
                self.stacktrace = format_exc()
                self.status = "error"
                return

            self.status = "moving"
            dir = dirname(target_path)
            if not exists(dir):
                mkdir(dir)
            move(tmp_path, target_path)

        self.status = "exited"
