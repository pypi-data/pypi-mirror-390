import pytest

from rick.resource.stream import SliceReader, MultiPartReader


class ByteArraySlice(SliceReader):
    def __init__(self, value_list: list):
        """
        Byte list slice, used for testing purposes
        :param value_list: list of values (<128 each)
        """
        super().__init__(value_list, len(value_list))

    def read(self, offset=0, length=-1):
        if length < 0:
            length = self.size
        end_ofs = offset + length
        return self.identifier[offset:end_ofs]


fixed_dataset = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25],
    [26, 27, 28, 29, 30],
]

variable_dataset = [
    [1],
    [2, 3, 4],
    [5, 6, 7, 8, 9, 10, 11],
    [12, 13, 14, 15],
    [16, 17, 18, 19, 20, 21, 22],
    [23, 24, 25],
    [26],
    [27, 28],
    [29, 30],
]

offset_results = [
    (  # complete read
        [0, -1],
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
    ),
    (  # complete read
        [0, 30],
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
    ),
    (  # complete read, past existing values
        [0, 40],
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
    ),
    (  # partial read to the end
        [2, -1],
        [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
    ),
    ([29, -1], [30]),  # partial read to the end
    ([7, 3], [8, 9, 10]),  # partial read, all in 2nd chunk
    ([5, 5], [6, 7, 8, 9, 10]),  # partial read, complete 2nd chunk
    (  # partial read, complete 2nd chunk and part 3rd chunk
        [5, 6],
        [6, 7, 8, 9, 10, 11],
    ),
    ([8, 5], [9, 10, 11, 12, 13]),  # partial read, middle of 2 blocks
    ([8, 5], [9, 10, 11, 12, 13]),  # partial read, middle of 2 blocks
    (  # partial read, two full blocks
        [10, 20],
        [
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        ],
    ),
]


@pytest.mark.parametrize("src,results", [(fixed_dataset, offset_results)])
def test_multipart_stream_fixed(src: list, results: list):
    parts = []
    for element in src:
        parts.append(ByteArraySlice(element))

    stream = MultiPartReader(parts=parts)

    for record in offset_results:
        offsets, expected = record
        result = []
        for r in stream.read(offsets[0], offsets[1]):
            result.extend(r)
        assert result == expected


@pytest.mark.parametrize("src,results", [(variable_dataset, offset_results)])
def test_multipart_stream_variable(src: list, results: list):
    parts = []
    for element in src:
        parts.append(ByteArraySlice(element))

    stream = MultiPartReader(parts=parts)

    for record in offset_results:
        offsets, expected = record
        result = []
        for r in stream.read(offsets[0], offsets[1]):
            result.extend(r)
        assert result == expected


@pytest.mark.parametrize("src,results", [(variable_dataset, offset_results)])
def test_multipart_stream_seek(src: list, results: list):
    parts = []
    for element in src:
        parts.append(ByteArraySlice(element))

    stream = MultiPartReader(parts=parts)

    # reverse results, force seek
    offset_results.reverse()
    for record in offset_results:
        offsets, expected = record
        result = []
        stream.seek(offsets[0])
        for r in stream.read(offsets[0], offsets[1]):
            result.extend(r)
        assert result == expected
