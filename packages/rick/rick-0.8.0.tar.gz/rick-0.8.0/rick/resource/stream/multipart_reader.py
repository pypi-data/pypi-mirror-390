from pathlib import Path
from io import BytesIO, SEEK_SET


class SliceReader:
    def __init__(self, identifier, size: int = 0):
        self.identifier = identifier
        self.size = size

    def read(self, offset=0, length=-1):
        pass


class FileSlice(SliceReader):
    def __init__(self, file_path: str):
        file = Path(file_path)
        if not file.is_file():
            raise ValueError("FileSlice: Invalid file object: {}".format(file))
        stat = file.stat()
        super().__init__(file, size=stat.st_size)

    def read(self, offset=0, length=-1):
        with open(self.identifier, "rb") as f:
            if offset > 0:
                f.seek(offset)
            return f.read(length)


class BytesIOSlice(SliceReader):
    def __init__(self, buf: BytesIO):
        super().__init__(buf, size=buf.getbuffer().nbytes)

    def read(self, offset=0, length=-1):
        self.identifier.seek(offset)
        return self.identifier.read(length)


class MultiPartReader:
    def __init__(self, parts: list = None):
        self.opened = False
        self.offset = -1

        if not parts:
            parts = []

        # compute size
        size = 0
        for p in parts:
            size += p.size

        self.parts = parts
        self.size = size

    def seek(self, offset: int, whence: int = 0) -> int:
        """
        Implements seeking support on the stream
        :param offset:
        :param whence:
        :return:
        """
        if whence != SEEK_SET:
            raise ValueError("MultiPartReader.seek() only supports SEEK_SET")

        if offset < 0:
            raise ValueError("MultiPartReader.seek() offset cannot be negative")

        if offset > self.size:
            self.offset = self.size
        self.offset = offset
        return self.offset

    def seekable(self) -> bool:
        return True

    def read(self, offset: int = None, length=-1):
        """
        Read from stream

        Example:

        reader = MultiPartReader(parts=my_part_list)
        with open('out_file', 'wb') as dest:
            for buf in reader.reader():
                dest.write(buf)

        :param offset:
        :param length:
        :return: yielded multiple buffers
        """
        if offset is None:
            if self.offset == -1:
                offset = 0
            else:
                offset = self.offset
        if offset < 0:
            raise ValueError("MultiPartReader:read(): negative offset is not supported")
        if length < 0:
            length = self.size

        ofs_current = 0
        ofs_end = offset + length
        for p in self.parts:
            run = 0

            ofs_end_part = ofs_current + p.size
            ofs_start = 0
            size = p.size

            # left boundary
            if offset < ofs_end_part:
                # check if its starting part, if so calculate start offset
                if offset >= ofs_current:
                    ofs_start = offset - ofs_current
                    run = 1
                    size = p.size - ofs_start

            # check if it is end block
            if ofs_end >= ofs_current:
                if ofs_end < ofs_end_part:
                    run = 3
                    size = ofs_end - ofs_current
                    if ofs_start > 0:
                        size = size - ofs_start

                # if it is a middle block
                elif ofs_current >= offset:
                    run = 2

            if run > 0:
                yield p.read(ofs_start, size)
                self.offset += size
            if run == 3:
                return

            ofs_current += p.size
