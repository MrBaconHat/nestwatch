import json
from .watcher import Watcher


class JSONWatcher(Watcher):
    def _serialize(self):
        with open(self.file_path, "r") as f:
            return json.load(f)