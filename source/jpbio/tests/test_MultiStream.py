import unittest
from MultiStream import MultiStream
import io

class TestCreateMultiStream(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'tests/temp'
        self.test_prefix = 'pre_'
        self.test_suffix = '_post'
        self.test_ext = '.tmp'
        self.ms = MultiStream(
            prefix=self.test_prefix, 
            suffix = self.test_suffix,
            extension = self.test_ext,
            directory=self.test_dir
            )

    def test_multistream_created(self):
        self.assertIsInstance(self.ms, MultiStream)

    def test_addTag(self):
        self.ms.addTag('tag')
        self.assertIsNone(self.ms.getStream('tag'))

    def test_getStream(self):
        self.ms.addTag('A')
        self.ms.open()
        stream_A = self.ms.getStream('A')
        self.assertIsNotNone(stream_A)
        self.assertIsInstance(stream_A, io.IOBase)
        self.ms.close()

    def test_getFilename(self):
        tag = 'tag'
        predicted_filename = self.test_prefix + tag + self.test_suffix + self.test_ext
        self.assertEquals(self.ms.getFileName(tag), predicted_filename)

    def test_write_to_streams(self):
        self.ms.addTag('A')
        self.ms.addTag('B')
        self.ms.open()
        self.ms.writeToStream('A', 'aaaaa')
        self.ms.writeToStream('B', 'bbbbb')
        self.ms.close()
        with open(self.ms.getFilePath('A')) as f_A, open(self.ms.getFilePath('B')) as f_B:
            data = f_A.read()
            self.assertEquals(data, 'aaaaa')
            self.assertNotEqual(data, 'xxxxx')
            data = f_B.read()
            self.assertEquals(data, 'bbbbb')
            self.assertNotEqual(data, 'xxxxx')

if __name__ == '__main__':
    unittest.main()
