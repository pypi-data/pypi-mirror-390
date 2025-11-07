from io import BytesIO
from typing import Union
from rick.resource.stream import MultiPartReader, FileSlice


class FilePart(FileSlice):
    pass


class FileReader(MultiPartReader):
    def __init__(
        self, parts: list, name="", content_type="application/octet-stream", **kwargs
    ):
        """
        Initialize filereader

        Node: undefined named parameters are added as properties of the object

        :param parts: stream part list
        :param name: file name
        :param content_type: mime type
        :param kwargs: optional named parameters to be added as properties of the object
        """
        self.name = name
        self.content_type = content_type
        reserved_names = dir(self)
        for k, v in kwargs.items():
            if k in reserved_names:
                raise ValueError(
                    "FileReader: invalid custom property name {}; property already exists".format(
                        k
                    )
                )
            setattr(self, k, v)
        super().__init__(parts=parts)

    def read_block(self, offset=0, limit=-1) -> BytesIO:
        result = BytesIO()
        for r in self.read(offset, limit):
            result.write(r)
        return result

    def read_chunked(self, block_size: int) -> BytesIO:
        blocks, reminder = divmod(self.size, block_size)
        ofs = 0
        while blocks > 0:
            buf = self.read_block(ofs, block_size)
            buf.seek(0)
            yield buf
            ofs += block_size
            blocks -= 1

        if reminder > 0:
            buf = self.read_block(ofs, reminder)
            buf.seek(0)
            yield buf
