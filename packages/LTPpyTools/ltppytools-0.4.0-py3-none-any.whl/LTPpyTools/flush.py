import sys

class flush:
    @classmethod
    def __init__(self):
        self.goflush = False
    def init(self):
        self.goflush = True
    def flush(self,name):
        if self.goflush:False
        print("pls run flush.init.")

        sys.stdout.write(name)
        sys.stdout.flush()