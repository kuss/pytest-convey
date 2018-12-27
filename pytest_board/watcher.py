from .utils import flush_q

from queue import Queue, Empty

import os
import sys
import time

from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileMovedEvent, FileDeletedEvent
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

WATCHED_EVENTS = [FileModifiedEvent, FileCreatedEvent, FileMovedEvent, FileDeletedEvent]


class FileSystemEventQueue(FileSystemEventHandler):
    def __init__(self, queue, extensions=['.py']):
        super(FileSystemEventQueue, self).__init__()
        self.queue = queue or Queue()
        self.extensions = extensions

    def on_any_event(self, event):
        print(event)
        if not isinstance(event, tuple(WATCHED_EVENTS)):
            return

        src_path = event.src_path
        dest_path = src_path
        if isinstance(event, FileMovedEvent):
            dest_path = os.path.relpath(event.dest_path)

        if not event.is_directory:
            src_ext_in = os.path.splitext(src_path)[1].lower() in self.extensions
            dest_ext_in = os.path.splitext(dest_path)[1].lower() in self.extensions
            if not src_ext_in and not dest_ext_in:
                return

        self.queue.put((type(event), src_path))


class Watcher(object):
    def __init__(self, directories=[], ignores=[], on_changed=None, on_exit=None):
        self.observer = PollingObserver()
        self.directories = directories
        self.ignores = ignores
        self.on_changed = on_changed
        self.on_exit = on_exit
        self.queue = Queue()
        self.basic_handler = FileSystemEventQueue(self.queue)
        for directory in self.directories:
            self.observer.schedule(self.basic_handler, path=directory, recursive=True)
        self.observer.start()

    @property
    def _has_diff(self):
        return not self.basic_handler.queue.empty()

    def _run_hook(self, hook, *args):
        if hook is not None:
            hook(*args)

    def run(self, polling_time=0.1):
        try:
            while True:
                if not self._has_diff:
                    time.sleep(polling_time)
                    continue
                self._run_hook(self.on_changed, list(self.basic_handler.queue.queue))
                flush_q(self.queue)
        except KeyboardInterrupt:
            self._run_hook(self.on_exit)
            raise KeyboardInterrupt
            return

if __name__ == '__main__':
    watcher = Watcher(directories=[os.getcwd()], on_changed=lambda x: print(x))
    try:
        while True:
            watcher.run()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exit caused by user interruption")
        sys.exit(1)
