from .watcher import Watcher
from .server import WebServer
from .testrunner import TestRunner

import pytest
import os
import sys
from multiprocessing import Process
import gevent

def main():
    web_server = WebServer()
    test_runner = TestRunner(
        before_run=web_server.notify_test_executing,
        on_completed=web_server.notify_test_completed,
    )
    web_server.set_test_runner(test_runner.notify)
    watcher = Watcher(
        directories=[os.getcwd()],
        on_changed=test_runner.notify,
    )

    workers = [
        Process(target=web_server.run),
        Process(target=test_runner.run),
        Process(target=watcher.run),
    ]

    try:
        # set first testing
        test_runner.notify('first')

        # start worker
        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()
    except:
        print('killing child process...')
        for worker in workers:
            worker.terminate()
        for worker in workers:
            worker.join()


if __name__ == '__main__':
    main()
