import zstandard as zstd

class Zreader:

    def __init__(self, file, chunk_size=16384):
        self.fh = open(file,'rb')
        self.chunk_size = chunk_size
        self.dctx = zstd.ZstdDecompressor()
        self.reader = self.dctx.stream_reader(self.fh)
        self.buffer = ''


    def readlines(self):
        while True:
            chunk = self.reader.read(self.chunk_size).decode('ISO-8859-1')
            if not chunk:
                break
            lines = (self.buffer + chunk).split("\n")
            
            for line in lines[:-1]:
                yield line

            self.buffer = lines[-1]