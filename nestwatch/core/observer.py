from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import asyncio


class FileSystemObserver(FileSystemEventHandler):
    def __init__(self, callback, file_path):
        self.callback = callback
        self.file_path = file_path

    def on_modified(self, event):
        if event.is_directory:
            return
        elif event.src_path == self.file_path:
            asyncio.run_coroutine_threadsafe(self.callback(), asyncio.get_event_loop())

    def start(self):
        observer = Observer()
        observer.schedule(self, path=".", recursive=False)
        observer.start()