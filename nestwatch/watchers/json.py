from ..core import FileSystemObserver

# --- Instances ---------------------
from ..core.events import Event

# --- Base Class --------------------
from .watcher import Watcher

import json

from typing import Callable


class JSONWatcher(Watcher):
    def _serialize(self):
        with open(self.file_path, "r") as f:
            return json.load(f)