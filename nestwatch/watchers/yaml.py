import aiofiles
import yaml

from .watcher import Watcher


class YAMLWatcher(Watcher):
    async def _serialize(self):
        async with aiofiles.open(self.file_path, "r") as f:
            content = await f.read()
            return yaml.safe_load(content)