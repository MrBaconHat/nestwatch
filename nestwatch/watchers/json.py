from ..core import FileSystemObserver

import json

from typing import Callable, Any


class JSONWatcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.observer = FileSystemObserver(self._on_modified, file_path)
        self.callback: Callable | None = None
        self.data = None

    async def _on_modified(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)

            # Compare the difference
            diff = self._diff(data)
            self.data = data

            if self.callback and isinstance(self.callback, Callable):
                await self.callback(diff)

    def _diff(self, data) -> dict:
        # Recursive function to find the difference between the old and new data
        # and then return the difference in the following format: e.g: {"old": {"key": "value"}, "new": {"key": "value"}}
        diff = {}
        if isinstance(data, dict):
            for key in data:
                if key not in self.data:
                    diff[key] = {"old": None, "new": data[key]}
                    
                elif data[key] != self.data.get(key):
                    diff[key] = {"old": self.data.get(key), "new": data[key]}

                elif isinstance(data[key], dict):
                    diff[key] = self._diff(data[key])

        return diff

    def on_change(self, func):
        """
        Sets the callback function to be called when the file is modified.
        """
        self.callback = func

    def start(self):
        """
        Starts the watcher.
        """
        self.observer.start()