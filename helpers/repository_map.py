from helpers.sha1 import calculate_sha1

from typing import Optional, Union, IO
from helpers.datastructs import SRL

from pathlib import Path
from io import BytesIO
import os


class Repository:
    def __init__(self):
        self._map = {}

    def add_file(
        self, file: os.PathLike, error_on_file_nonexistent: bool = True
    ) -> Optional[str]:
        if not error_on_file_nonexistent:
            if not os.path.exists(file):
                return None
        hash = self.get_hash_from_file_path(file)
        if hash:
            del self._map[hash]
        sha1 = calculate_sha1(file)
        file_path = str(file)
        if sha1 not in self._map.keys():
            self._map[sha1] = {"hash": sha1, "file": file_path}
        return sha1

    def add_bytes(self, data: Union[IO[bytes], bytes]):
        """
        Warning: cannot be updated!
        """
        sha1 = calculate_sha1(data)
        if sha1 not in self._map.keys():
            self._map[sha1] = {"hash": sha1, "file": data}

    def pop_hash(self, hash: str) -> Optional[bytes]:
        file_data = self.get_file(hash)
        if file_data:
            del self._map[hash]
        return file_data

    def update_file(self, file: os.PathLike):
        """
        Alias for add_file lol
        """
        self.add_file(file)

    def get_hash_from_file_path(self, file: os.PathLike) -> Optional[str]:
        input_path = os.path.abspath(file)
        for sha1, data in self._map.items():
            if type(data["file"]) != str:
                continue
            stored_path = os.path.abspath(data["file"])
            if input_path == stored_path:
                return sha1
        return None

    def get_file(self, hash: str) -> Optional[bytes]:
        item = self._map.get(hash, None)
        if item:
            file = item["file"]
            file_data = None
            if isinstance(file, (str, Path)):
                with open(file, "rb") as file:
                    file_data = file.read()
            elif isinstance(file, BytesIO):
                file_data = file.read()
            elif isinstance(file, bytes):
                file_data = file
            return file_data
        return None

    def get_srl(self, hash: str) -> Optional[SRL]:
        if hash in self._map.keys():
            return {"hash": hash, "url": f"/sonolus/repository/{hash}"}
        return None


repo = Repository()
