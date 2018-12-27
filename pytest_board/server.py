from gevent import monkey; monkey.patch_all()
import bottle
from bottle import request, response
from datetime import datetime

from multiprocessing import Queue
from queue import Empty

import os
import gevent
import json

TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), 'client')


class WebServer(object):
    def __init__(self, q=None, runner=None):
        self.q = q or Queue()
        self.runner = runner
        self.latest_status = 'idle'
        self.latest_result = {}

        bottle.route('/')(self.handle_home)
        bottle.route('/resources/<filepath:path>')(self.handle_serve_static)
        bottle.route('/status')(self.handle_status)
        bottle.route('/status/poll')(self.handle_status_poll)
        bottle.route('/watch')(self.handle_watch)
        bottle.route('/latest')(self.handle_latest)
        bottle.route('/execute')(self.handle_execute)

    def set_test_runner(self, runner):
        self.runner = runner

    def notify_test_executing(self):
        self.q.put(('executing', None))

    def notify_test_completed(self, result):
        self.q.put(('idle', json.dumps(result, default=lambda o: str(o))))

    def run(self):
        bottle.run(app=bottle.app(), host='127.0.0.1', port=8000, quiet=True)

    def handle_home(self):
        return bottle.static_file('index.html', root=TEMPLATE_ROOT)

    def handle_serve_static(self, filepath):
        return bottle.static_file(filepath, root=os.path.join(TEMPLATE_ROOT, 'resources'))

    def handle_status(self):
        return 'executing'

    def handle_status_poll(self):
        timeout = int(request.query.get('timeout', 120000)) / 1000
        try:
            status, result = self.q.get(timeout=timeout-10)
            self.latest_status = status
            if result is not None:
                self.latest_result = json.loads(result)
            return status
        except Empty:
            return 'idle'

    def handle_watch(self):
        return os.getcwd()

    def handle_latest(self):
        if 'tests' not in self.latest_result:
            return json.dumps({})

        revision = self.latest_result['created']
        packages = {}
        for test in self.latest_result['tests']:
            filename = os.path.basename(test['path'])
            dirname = os.path.dirname(test['path'])
            if dirname not in packages:
                packages[dirname] = dict(
                    PackageName=dirname,
                    Coverage=0.0,
                    Elapsed=0.0,
                    Outcome='passed',
                    BuildOutput='',
                    TestResults=[],
                )

            elapsed = test['setup']['duration'] + test['call']['duration'] + test['teardown']['duration']
            logs = [x['msg'] for x in test['setup']['log'] + test['call']['log'] + test['teardown']['log']]

            test_results = dict(
                File=filename,
                Line=test['lineno'],
                Message='<br/>'.join(logs),
                Passed=test['outcome']=='passed',
                Skipped=test['outcome']=='skipped',
                Stories=[],
                TestName=test['domain'],
                Error=test['call'].get('longrepr', ''),
                Elapsed=elapsed,
            )

            packages[dirname]['Elapsed'] += elapsed
            packages[dirname]['TestResults'].append(test_results)

        return json.dumps(dict(
            Packages=packages,
            Paused=False,
            Revision=revision,
        ))

    def handle_execute(self):
        if self.runner is not None:
            self.runner('web ui')

if __name__ == '__main__':
    server = WebServer(Queue())
    server.run()
