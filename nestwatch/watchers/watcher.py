from ..core import FileSystemObserver

# --- Instances ---------------------
from ..core.events import Event

import json
import asyncio
import traceback

from typing import Callable


class Watcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.observer = FileSystemObserver(self._on_modified, file_path)
        self.callback: Callable = None
        self.data = None

    def _serialize(self):
        raise NotImplementedError(
            f"Serialize for {self.file_path} is not implemented yet."
            f"Please implement the `serialize` method in the {self.__class__.__name__} class."
        )

    async def _call_serialize(self):
        if asyncio.iscoroutinefunction(self._serialize):
            return await self._serialize()

        return self._serialize()

    async def _on_modified(self):
        old = self.data or {}
        new = None
        try:
            new = await self._call_serialize()
            
        except Exception as e:
            traceback.print_exception(
                type(e), e, e.__traceback__
            )
            return

        added, removed, changed = self._diff(old, new)
        self.data = new

        if callable(self.callback):
            await self.callback(
                Event(
                    added,
                    removed,
                    changed,
                ))

    def _flatten(self, data, path=None):
        result = {}

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict):
                result.update(
                    self._flatten(value, current_path)
                )

            else:
                result[current_path] = value

        return result

    def _diff(self, old, new, path=None):
        added = {}
        removed = {}
        changed = {}

        path = path
        
        all_keys = set(old or {}) | set(new or {})
            
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in old:
                added.update(
                    self._flatten(
                        {key: new[key]}, path)
                )

            elif key not in new:
                removed.update(
                    self._flatten(
                        {key: old[key]}, path)
                )

            elif isinstance(old[key], dict) and isinstance(new[key], dict):
                added_, removed_, changed_ = self._diff(old[key], new[key], current_path)
                added.update(added_)
                removed.update(removed_)
                changed.update(changed_)

            elif isinstance(old[key], list) and isinstance(new[key], list):
                if (
                    len(old[key]) != len(new[key])
                    or old[key] != new[key]
                ):
                    changed[current_path] = {"old": old[key], "new": new[key]}

            elif old[key] != new[key]:
                changed[current_path] = {"old": old[key], "new": new[key]}


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
        self.data = await self._call_serialize()

        await self.observer.start()

    async def stop(self):
        """
        Stops the watcher.
        """
        await self.observer.stop()