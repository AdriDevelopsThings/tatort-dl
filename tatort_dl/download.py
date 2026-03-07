from os import mkdir, listdir
from os.path import exists, join
from queue import Queue
from shutil import rmtree
from sys import stdout
from time import sleep

import yt_dlp

from tatort_dl.api.episode import Episode
from tatort_dl.download_worker import DownloadWorker
from tatort_dl.utils import format_bytes


class Downloader:
    def __init__(
        self, dir: str, tmp: str, worker_count: int, concurrent_fragment_downloads: int
    ):
        self.tmp = tmp
        self.concurrent_fragment_downloads = concurrent_fragment_downloads
        self.worker_count = worker_count
        self.running = False

        self.__dir = dir
        self.__workers: list[DownloadWorker] = []

        if not exists(dir):
            mkdir(dir)
        if not exists(self.tmp):
            mkdir(self.tmp)

    def get_episode_dir(self, episode: Episode) -> str:
        return join(self.__dir, episode.meta.investigators[0])

    def get_episode_path(self, episode: Episode) -> str:
        return join(self.get_episode_dir(episode), episode.get_filename())

    def is_downloaded(self, episode: Episode) -> bool:
        episode_dir = self.get_episode_dir(episode)
        prefix = episode.get_prefix_filename()
        for file in listdir(episode_dir):
            if file.startswith(prefix):
                return True
        return False

    def download(self, download_queue: Queue[Episode]):
        self.running = True
        for i in range(self.worker_count):
            worker = DownloadWorker(self, download_queue)
            worker.start()
            self.__workers.append(worker)

        fc = True
        try:
            while self.__count_running_workers() > 0:
                self.__print_download_info(first_call=fc)
                fc = False

                for w in self.__workers:
                    if w.status == "error" and self.running:
                        self.running = False
                        print(
                            "\nException in one worker -> finishing remaining tasks, then exiting"
                        )
                        fc = True
                sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\nFinishing last jobs...")
            fc = True
            while self.__count_running_workers() > 0:
                self.__print_download_info(first_call=fc)
                fc = False
                sleep(1)
        finally:
            for w in self.__workers:
                if w.error:
                    print(f"Exception in worker: {w.error}, stacktrace:")
                    print(w.stacktrace)
                    print("Worker tried to download episode")
                    print(f"{w.current_episode}")
                    if w.current_episode and w.current_episode.ard:
                        print(f"Download url was: {w.current_episode.ard.download_url}")
                    print("")
            self.running = False
            self.__cleanup()

    def __print_download_info(self, first_call: bool = False):
        if not first_call:
            for i in range(self.worker_count + 1):
                stdout.write("\033[F")
                stdout.write("\033[K")

        print("Current state of workers:")

        title_length = (
            max(
                [
                    len(w.current_episode.meta.title)
                    for w in self.__workers
                    if w.current_episode
                ]
            )
            + 1
        )

        for worker in self.__workers:
            if worker.status == "starting":
                print("Worker is starting...")
                continue
            elif worker.status == "exited":
                print("Worker is finished")
                continue

            assert worker.current_episode
            episode_id = f"{worker.current_episode.meta.id: <4}"
            episode_title = worker.current_episode.meta.title.ljust(title_length)
            print(f"{episode_id}: {episode_title}: ", end="")
            if worker.status == "downloading":
                if worker.info_dict:
                    fragment = ""
                    if (
                        "fragment_index" in worker.info_dict
                        and "fragment_count" in worker.info_dict
                    ):
                        fi = worker.info_dict["fragment_index"]
                        fc = worker.info_dict["fragment_count"]
                        fragment = f" ({fi:03}/{fc:03})"
                    downloaded_bytes = worker.info_dict["downloaded_bytes"]
                    total_bytes = (
                        worker.info_dict["total_bytes_estimate"]
                        if "total_bytes_estimate" in worker.info_dict
                        else None
                    )
                    eta = worker.info_dict["eta"]
                    progress = worker.info_dict["_percent"]
                    eta = " ETA " + f"{round(eta)}s" if eta else ""
                    bytes = (
                        format_bytes(downloaded_bytes)
                        + f" / {format_bytes(total_bytes)}"
                        if total_bytes
                        else ""
                    )
                    print(f"{progress: 6.02f}%{fragment}{eta} {bytes}")
                else:
                    print("Downloading...")
            elif worker.status == "error":
                error_info = f": {str(worker.error)}" if worker.error else ""
                print(f"Error{error_info}")
            elif worker.status == "finishing":
                print("Finishing download...")
            elif worker.status == "moving":
                print("Moving file to destination...")

            stdout.flush()

    def __cleanup(self):
        rmtree(self.tmp)

    def __count_running_workers(self) -> int:
        running_workers = [
            w for w in self.__workers if w.status != "exited" and w.status != "error"
        ]
        return len(running_workers)
