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
            added, removed, changed = self._diff(
                self.data or {},
                data
            )
            self.data = data

            if callable(self.callback):
                await self.callback(added, removed, changed)

    def _diff(self, old, new):
        # Recursive function to find the difference between the old and new data
        # and then return the difference in the following format: {"added": {"key": "value"}, "removed": {"key": "value"}, "changed": {"key": {"old": "value", "new": "value"}}}

        added = {}
        removed = {}
        changed = {}
        
        all_keys = set(old) | set(new)
        for key in all_keys:
            if key not in old:
                added[key] = new[key]

            elif key not in new:
                removed[key] = old[key]

            elif old[key] != new[key]:
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    nested_added, nested_removed, nested_changed = self._diff(old[key], new[key])

                    changed[key] = {
                        "added": nested_added,
                        "removed": nested_removed,
                        "changed": nested_changed
                    }

                else:
                    changed[key] = {"old": old[key], "new": new[key]}


        return added, removed, changed
        
        

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