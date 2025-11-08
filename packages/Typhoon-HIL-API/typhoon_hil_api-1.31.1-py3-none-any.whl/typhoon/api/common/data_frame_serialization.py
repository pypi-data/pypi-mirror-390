from base64 import decodebytes, encodebytes
from io import BytesIO

from pandas import DataFrame, read_feather

SERIALIZE_OPTS = {"compression": "lz4", "compression_level": 0}


def serialize_data_frame(data_frame: DataFrame) -> str:
    bytes_buffer = BytesIO()
    data_frame.to_feather(bytes_buffer, **SERIALIZE_OPTS)
    bytes_buffer.seek(0)
    bytes_content = bytes_buffer.read()
    return encodebytes(bytes_content).decode("utf-8")


def deserialize_data_frame(data_content: str) -> DataFrame:
    return read_feather(BytesIO(decodebytes(data_content.encode("utf-8"))))


def atest_serialize_data_frame():
    data_frame1 = DataFrame({"Sales-By-Month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    print(data_frame1)
    data = serialize_data_frame(data_frame1)
    data_frame2 = deserialize_data_frame(data)

    print(data_frame1.equals(data_frame2))
