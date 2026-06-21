import json
import aiofiles
from .watcher import Watcher


class JSONWatcher(Watcher):
    async def _serialize(self):
        async with aiofiles.open(self.file_path, "r") as f:
            content = await f.read()
            return json.loads(content)