from hashlib import blake2b
from json import dumps, loads
from os import mkdir, remove
from os.path import exists, join
from time import time
from typing import Any, Optional, TypeAlias

from platformdirs import user_cache_dir

CACHE_APPNAME = "tatort-dl"
CACHE_APPAUTHOR = "AdriDevelopsThings"


class Cache:
    def __init__(self):
        self.__cache_dir = user_cache_dir(CACHE_APPNAME, CACHE_APPAUTHOR)
        if not exists(self.__cache_dir):
            mkdir(self.__cache_dir)

    def __key_hash(self, key) -> str:
        return blake2b(dumps(key).encode("utf-8")).hexdigest()

    def __key_path(self, key) -> str:
        return join(self.__cache_dir, self.__key_hash(key))

    def get(self, key) -> Optional[Any]:
        p = self.__key_path(key)
        if not exists(p):
            return None
        with open(p) as file:
            l = file.readline()
            ex = float(l[:-1])
            if time() >= ex:
                remove(p)
                return None
            return loads(file.read())

    def set(self, key, value: Any, ex: int):
        with open(self.__key_path(key), "w") as file:
            file.write(f"{time() + ex}\n")
            file.write(dumps(value))


cache = Cache()
