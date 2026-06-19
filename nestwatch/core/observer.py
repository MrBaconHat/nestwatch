from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import asyncio
import time


class FileSystemObserver(FileSystemEventHandler):
    def __init__(self, callback, file_path):
        self.callback = callback
        self.file_path = file_path
        self.observer = Observer()

        self.last_called = 0

    def on_modified(self, event):
        if time.time() - self.last_called < 0.2:
            return
        self.last_called = time.time()
            
        if event.is_directory:
            return
            
        elif event.src_path == self.file_path:
            asyncio.run_coroutine_threadsafe(self.callback(), loop=self.loop)

    async def start(self):
        self.loop = asyncio.get_running_loop()
        self.observer.schedule(self, path=self.file_path, recursive=False)
        self.observer.start()