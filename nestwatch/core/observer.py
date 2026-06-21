from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import asyncio
import time

from pathlib import Path


class FileSystemObserver(FileSystemEventHandler):
    def __init__(self, callback, file_path):
        self.callback = callback
        self.file_path = Path(file_path).resolve()
        self.directory = self.file_path.parent
        
        self.observer = Observer()

        self.last_called = 0

    def _run_thread_loop(self):
        future = asyncio.run_coroutine_threadsafe(self.callback(), loop=self.loop)
        future.add_done_callback(lambda f: f.exception())

    def _handle(self, event):
        if time.time() - self.last_called < 0.2:
            return
        self.last_called = time.time()
            
        if event.is_directory:
            return
            
        if Path(event.src_path) == self.file_path:
            self._run_thread_loop()

    def on_modified(self, event):
        self._handle(event)

    def on_created(self, event):
        self._handle(event)

    def on_moved(self, event):
        if time.time() - self.last_called < 0.2:
            return
        self.last_called = time.time()
        
        if event.is_directory:
            return

        if Path(event.dest_path) != self.file_path:
            return

        self._run_thread_loop()

    async def start(self):
        self.loop = asyncio.get_running_loop()
        self.observer.schedule(self, path=str(self.directory), recursive=False)
        self.observer.start()

    async def stop(self):
        self.observer.stop()
        self.observer.join()