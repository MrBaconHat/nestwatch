from ..core import FileSystemObserver

# --- Instances ---------------------
from ..core.events import Event

import json

from typing import Callable


class JSONWatcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.observer = FileSystemObserver(self._on_modified, file_path)
        self.callback: Callable = None
        self.data = None

    async def _on_modified(self):
        old = self.data
        with open(self.file_path, "r") as f:
            new_data = json.load(f)

            # Compare the difference
            added, removed, changed = self._diff(
                self.data or {},
                new_data
            )
            self.data = new_data
            

            if callable(self.callback):
                await self.callback(
                    Event(
                        added,
                        removed,
                        changed,
                        old,
                        new_data
                    )
                )

    def _diff(self, old, new, path=None):
        added = {}
        removed = {}
        changed = {}

        path = path
        
        all_keys = set(old or {}) | set(new or {})
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in old:
                added[current_path] = new[key]

            elif key not in new:
                removed[current_path] = old[key]

            elif isinstance(old[key], dict) and isinstance(new[key], dict):
                added_, removed_, changed_ = self._diff(old[key], new[key], current_path)
                added.update(added_)
                removed.update(removed_)
                changed.update(changed_)

            elif old[key] != new[key]:
                changed[current_path] = {
                    "old": old[key],
                    "new": new[key]
                }


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

    async def stop(self):
        """
        Stops the watcher.
        """
        await self.observer.stop()