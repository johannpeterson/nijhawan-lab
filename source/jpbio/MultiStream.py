import os, weakref

class MultiStream:

    def __init__(self, tags=[], prefix='', suffix='', extension='.txt', mode='w', directory=''):
        self._streams = {t:None for t in tags}
        self.prefix = prefix
        self.suffix = suffix
        self.extension = extension
        self.mode = mode
        self.directory = directory
        self._finalizer = weakref.finalize(self, self.close)

    def remove(self):
        self._finalizer()

    @property
    def removed(self):
        return not self._finalizer.alive

    def addTag(self, tag):
        if tag not in self._streams:
            self._streams[tag] = None
    
    def open(self):
        # TODO: use the directory argument
        for tag in self._streams:
            filename = os.path.join(
                self.directory,
                self.prefix + tag + self.suffix + self.extension)
            self._streams[tag] = open(filename, self.mode)

    def close(self):
        for f in self._streams:
            self._streams[f].close()

    def getStream(self, tag):
        try:
            return self._streams[tag]
        except KeyError:
            return None
