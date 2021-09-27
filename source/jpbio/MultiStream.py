class MultiStream:

    def __init__(self, tags=[], prefix='', suffix='', extension='.txt', mode='w', directory=''):
        self._streams = {t:None for t in tags}
        self.prefix = prefix
        self.suffix = suffix
        self.extension = extension
        self.mode = mode
        self.directory = directory
        self._finalizer = weakref.finalize(self, self.close, self._streams)

    def remove(self):
        self._finalizer()

    @property
    def removed(self):
        return not self._finalizer.alive

    def addTag(tag):
        if tag not in self._streams:
            self.streams[tag] = None
    
    def open():
        # TODO: use the directory argument
        for tag in self.streams:
            filename = self.prefix + tag + self.suffix + self.extension
            self.streams[tag] = open(filename, self.mode)

    def close(stream_dict=self.streams):
        for f in stream.dict:
            stream_dict[f].close()
