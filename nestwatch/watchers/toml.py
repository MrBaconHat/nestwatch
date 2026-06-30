import aiofiles
import tomllib

from .watcher import Watcher

class TOMLWatcher(Watcher):
    async def _serialize(self):
        async with aiofiles.open(self.file_path, "rb") as f:
            content = await f.read()
            return tomllib.loads(content.decode("utf-8"))