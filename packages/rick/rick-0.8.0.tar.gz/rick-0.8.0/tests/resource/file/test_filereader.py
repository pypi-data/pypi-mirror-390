import os
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from rick.crypto import sha256_hash
from rick.resource.file.filereader import FilePart, FileReader


def create_test_file(folder_name, size):
    """
    Generate a file named filereader_test.bin filled with random garbage

    :param folder_name:
    :param size:
    :return:
    """
    fname = Path(folder_name) / Path("filereader_test.bin")
    if fname.exists():
        fname.unlink()

    buf = BytesIO()
    buf.write(os.urandom(size))

    # garbage out
    with open(fname, "wb") as dest:
        buf.seek(0)
        dest.write(buf.read())

    return fname, sha256_hash(buf)


def slice_file(src, block_size, folder_name, part_name="part_{}.bin") -> List:
    """
    Slice a file into several files with block_size bytes
    :param src:
    :param block_size:
    :param folder_name:
    :param part_name:
    :return:
    """
    result = []
    src_file = Path(src)
    folder = Path(folder_name)
    fsize = os.stat(src_file).st_size

    count = 0
    blocks, rem = divmod(fsize, block_size)
    with open(src_file, "rb") as f_in:
        while blocks > 0:
            count += 1
            dest_file = folder / Path(part_name.format(count))
            if dest_file.exists():
                dest_file.unlink()

            result.append(dest_file)
            with open(dest_file, "wb") as f_out:
                buf = f_in.read(block_size)
                f_out.write(buf)
                blocks -= 1

        if rem > 0:
            count += 1
            dest_file = folder / Path(part_name.format(count))
            if dest_file.exists():
                dest_file.unlink()

            result.append(dest_file)
            with open(dest_file, "wb") as f_out:
                buf = f_in.read(rem)
                f_out.write(buf)
                blocks -= 1

    return result


def test_filereader():
    total_size = 16384 * 1024
    with TemporaryDirectory() as folder:
        # generate temporary file with garbage
        fname, fhash = create_test_file(folder, total_size)  # 16mb
        # slice file in chunks
        chunks = slice_file(fname, 1000 * 1024, folder)  # ~1mb

        parts = []
        for c in chunks:
            parts.append(FilePart(c))

        f = FileReader(parts=parts)

        # read chunked as a single block
        for buf in f.read_chunked(total_size):
            assert sha256_hash(buf) == fhash

        # read in 4kb blocks
        final_buf = BytesIO()
        bs_size = 4000
        for buf in f.read_chunked(bs_size):
            final_buf.write(buf.read())

        assert sha256_hash(final_buf) == fhash


def test_filereader_attrs():
    total_size = 16384 * 1024
    with TemporaryDirectory() as folder:
        # generate temporary file with garbage
        fname, fhash = create_test_file(folder, total_size)  # 16mb
        # slice file in chunks
        chunks = slice_file(fname, 1000 * 1024, folder)  # ~1mb

        parts = []
        for c in chunks:
            parts.append(FilePart(c))

        attrs = {"key": "value"}
        f = FileReader(parts=parts, attributes=attrs, record=folder)
        assert f.attributes == attrs
        assert f.record == folder
