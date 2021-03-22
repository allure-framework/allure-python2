# -*- coding: UTF-8 -*-
import io
import sys


class Tee(object):
    def __init__(self):
        self.memory = io.StringIO()
        self.origin_stdout = None

    def start(self):
        self.origin_stdout, sys.stdout = sys.stdout, self

    def close(self):
        if self.origin_stdout:
            sys.stdout = self.origin_stdout
        self.flush()

    def getvalue(self, *args, **kwargs):
        return self.memory.getvalue(*args, **kwargs)

    def write(self, data):
        self.memory.write(data)
        if self.origin_stdout:
            self.origin_stdout.write(data)

    def flush(self):
        self.memory.seek(0)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()