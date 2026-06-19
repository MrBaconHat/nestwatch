from ..core import FileSystemObserver

import json

from typing import Callable


class JSONWatcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.observer = FileSystemObserver(self._on_modified, file_path)
        self.callback: Callable = None
        self.data = None

    async def _on_modified(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)

            # Compare the difference
            diff = self._diff(data, main=True)
            self.data = data

            if callable(self.callback):
                await self.callback(diff)

    def _diff(self, data, main=True) -> dict:
        # Recursive function to find the difference between the old and new data
        # and then return the difference in the following format: e.g: {"old": {"key": "value"}, "new": {"key": "value"}}
        diff = {}
        if isinstance(data, dict):
            for key in data:
                if self.data is None or key not in self.data:
                    diff[key] = {"old": None, "new": data[key]}

                elif isinstance(data[key], dict):
                    diff[key] = self._diff(data[key], main=False)
                    
                elif data[key] != self.data.get(key):
                    diff[key] = self.data.get(key)


        if main:
            new_diff = {"old": {}, "new": {}}
            for key in diff:
                new_diff["old"][key] = self.data.get(key)
                new_diff["new"][key] = data.get(key)
                return new_diff

        return diff

    def on_change(self, func):
        """
        Sets the callback function to be called when the file is modified.
        """
        self.callback = func

    async def start(self):
        """
        Starts the watcher.
        """

        # Up-to-date the cache before starting
        with open(self.file_path, "r") as f:
            self.data = json.load(f)

        await self.observer.start()