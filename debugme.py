import multiprocessing
import os
import time
from multiprocessing import freeze_support

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from datetime import datetime, timedelta

import runpy


def run_py():
    runpy.run_path(path_name='main.py')


def rerun_script():
    global p
    p.terminate()
    p = multiprocessing.Process(target=run_py)
    p.start()


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = datetime.now()

    def on_modified(self, event):
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        path: str = event.src_path.replace("~", "")
        if path.endswith(".py"):
            os.system('cls')
            rerun_script()


if __name__ == "__main__":
    freeze_support()
    p = multiprocessing.Process(target=run_py)
    p.start()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
