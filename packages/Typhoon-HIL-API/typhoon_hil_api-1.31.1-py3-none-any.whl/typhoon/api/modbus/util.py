#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import struct


def bool_list_to_int(bool_list):
    """
    Converts given bool list to the int number.
    First element in given bool list is used as MSB.

    Args:
        bool_list(list): List of booleans.
    Returns:
        An integer.
    """
    # Convert to list of integers (0 or 1).
    bit_list = list(map(int, bool_list))

    num = 0
    for bit in bit_list:
        num = (num << 1) | bit
    return num


def uint16_to_int16(uint16, big_endian=True):
    """
    Convert unsigned int (16 bit) number to signed int (16 bit) number.

    :param uint16: unsigned int (16 bit) number
    :type uint16: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: singed int (16 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}H", uint16)

    # unpack byte string to int16
    return struct.unpack(f"{endianness}h", byte_str)[0]


def uint32_to_int32(uint32, big_endian=True):
    """
    Convert unsigned int (32 bit) number to signed int (32 bit) number.

    :param uint32: unsigned int (32 bit) number
    :type uint32: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: singed int (32 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}I", uint32)

    # unpack byte string to int32
    return struct.unpack(f"{endianness}i", byte_str)[0]


def uint64_to_int64(uint64, big_endian=True):
    """
    Convert unsigned int (64 bit) number to signed int (64 bit) number.

    :param uint64: unsigned int (64 bit) number
    :type uint64: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: singed int (64 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}Q", uint64)

    # unpack byte string to int64
    return struct.unpack(f"{endianness}q", byte_str)[0]


def uint32_to_float(uint32, big_endian=True):
    """
    Convert unsigned int (32 bit) number to float number.

    :param uint32: unsigned int (32 bit) number
    :type uint32: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: float number
    :rtype: float
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}I", uint32)

    # unpack byte string to float
    return struct.unpack(f"{endianness}f", byte_str)[0]


def uint64_to_double(uint64, big_endian=True):
    """
    Convert unsigned int (64 bit) number to float number (64 bit).

    :param uint64: unsigned int (64 bit) number
    :type uint64: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: float number (64 bit)
    :rtype: float
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}Q", uint64)

    # unpack byte string to float
    return struct.unpack(f"{endianness}d", byte_str)[0]


def float_to_uint32(float_num, big_endian=True):
    """
    Convert float number to unsigned int (32 bit) number.

    :param float_num: float number
    :type float_num: float
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: int number
    :rtype: int
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}f", float_num)

    # unpack byte string to uint32
    return struct.unpack(f"{endianness}I", byte_str)[0]


def double_to_uint64(double_num, big_endian=True):
    """
    Convert float number (64 bit) to unsigned int (64 bit) number.

    :param double_num: float number (64 bit)
    :type double_num: float
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: int number
    :rtype: int
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}d", double_num)

    # unpack byte string to uint64
    return struct.unpack(f"{endianness}Q", byte_str)[0]


def int16_to_uint16(int16, big_endian=True):
    """
    Convert signed int (16 bit) number to unsigned int (16 bit) number.

    :param int16: signed int (16 bit) number
    :type int16: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: unsigned int (16 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}h", int16)

    # unpack byte string to uint16
    return struct.unpack(f"{endianness}H", byte_str)[0]


def int32_to_uint32(int32, big_endian=True):
    """
    Convert signed int (32 bit) number to unsigned int (32 bit) number.

    :param int32: signed int (32 bit) number
    :type int32: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: unsigned int (32 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}i", int32)

    # unpack byte string to uint32
    return struct.unpack(f"{endianness}I", byte_str)[0]


def int64_to_uint64(int64, big_endian=True):
    """
    Convert signed int (64 bit) number to unsigned int (64 bit) number.

    :param int64: signed int (64 bit) number
    :type int64: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: unsigned int (64 bit) number
    :rtype: int
    """
    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}q", int64)

    # unpack byte string to uint64
    return struct.unpack(f"{endianness}Q", byte_str)[0]


def int32_to_uint16_list(int32, big_endian=True):
    """
    Converts signed int number (32 bit) to list of two unsigned int (16 bit) numbers.

    :param int32: signed int number (32 bit)
    :type int32: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with two unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}i", int32)

    # unpack byte string to list of two uin16 numbers
    return list(struct.unpack(f"{endianness}HH", byte_str))


def int64_to_uint16_list(int64, big_endian=True):
    """
    Converts signed int number (64 bit) to list of four unsigned int (16 bit) numbers.

    :param int64: signed int number (64 bit)
    :type int64: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with four unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}q", int64)

    # unpack byte string to list of two uin16 numbers
    return list(struct.unpack(f"{endianness}HHHH", byte_str))


def uint32_to_uint16_list(uint32, big_endian=True):
    """
    Converts unsigned int number (32 bit) to list of two unsigned int (16 bit) numbers.

    :param uint32: unsigned int number (32 bit)
    :type uint32: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with two unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}I", uint32)

    # unpack byte string to list of two uin16 numbers
    return list(struct.unpack(f"{endianness}HH", byte_str))


def uint64_to_uint16_list(uint64, big_endian=True):
    """
    Converts unsigned int number (64 bit) to list of four unsigned int (16 bit) numbers.

    :param uint64: unsigned int number (64 bit)
    :type uint64: int
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with four unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}Q", uint64)

    # unpack byte string to list of two uin16 numbers
    return list(struct.unpack(f"{endianness}HHHH", byte_str))


def float_to_uint16_list(float_num, big_endian=True):
    """
    Converts float number to list of two unsigned int (16 bit) numbers.

    :param float_num: float number
    :type float_num: float
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with two unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}f", float_num)

    # unpack byte string to list of two uin16 numbers
    return list(struct.unpack(f"{endianness}HH", byte_str))


def double_to_uint16_list(double_num, big_endian=True):
    """
    Converts float number (64 bit) to list of four unsigned int (16 bit) numbers.

    :param double_num: float number (64 bit)
    :type double_num: float
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: list with four unsigned int (16 bit) values
    :rtype: list
    """

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}d", double_num)

    # unpack byte string to list of uint16
    return list(struct.unpack(f"{endianness}HHHH", byte_str))


def uint16_list_to_float(int_list, big_endian=True):
    """
    Converts list of two unsigned int (16 bit) numbers to float number.

    :param int_list: list with two unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: float number
    :rtype: float
    """

    if len(int_list) != 2:
        raise ValueError(
            "Parameter 'int_list' must be list with two unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HH", *int_list)

    # unpack byte string to float
    return struct.unpack(f"{endianness}f", byte_str)[0]


def uint16_list_to_double(int_list, big_endian=True):
    """
    Converts list of four unsigned int (16 bit) numbers to float number (64 bit).

    :param int_list: list with four unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: float number (64 bit)
    :rtype: float
    """

    if len(int_list) != 4:
        raise ValueError(
            "Parameter 'int_list' must be list with four unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HHHH", *int_list)

    # unpack byte string to double
    return struct.unpack(f"{endianness}d", byte_str)[0]


def uint16_list_to_int32(int_list, big_endian=True):
    """
    Converts list of two unsigned int (16 bit) numbers to signed int (32 bit).

    :param int_list: list with two unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: signed int number (32 bit)
    :rtype: int
    """

    if len(int_list) != 2:
        raise ValueError(
            "Parameter 'int_list' must be list with two unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HH", *int_list)

    # unpack byte string to int32
    return struct.unpack(f"{endianness}i", byte_str)[0]


def uint16_list_to_int64(int_list, big_endian=True):
    """
    Converts list of four unsigned int (16 bit) numbers to signed int number (64 bit).

    :param int_list: list with four unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :return: signed int number (64 bit)
    :rtype: int
    """

    if len(int_list) != 4:
        raise ValueError(
            "Parameter 'int_list' must be list with four unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HHHH", *int_list)

    # unpack byte string to double
    return struct.unpack(f"{endianness}q", byte_str)[0]


def uint16_list_to_uint32(int_list, big_endian=True):
    """
    Converts list of two unsigned int (16 bit) numbers to unsigned int (32 bit) number.

    :param int_list: list with two unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :returns: unsigned int (32 bit)
    :rtype: int
    :raise: ValueError: in case ``int_list`` length is != 2
    """

    if len(int_list) != 2:
        raise ValueError(
            "Parameter 'int_list' must be list with two unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HH", *int_list)

    # unpack byte string to double
    return struct.unpack(f"{endianness}I", byte_str)[0]


def uint16_list_to_uint64(int_list, big_endian=True):
    """
    Converts list of four unsigned int (16 bit) numbers to unsigned int (64 bit) number.

    :param int_list: list with four unsigned int (16 bit) values
    :type int_list: list
    :param big_endian: True for big endian/False for little (optional)
    :type big_endian: bool
    :returns: unsigned int (64 bit)
    :rtype: int
    :raise: ValueError: in case ``val_list`` length is != 4
    """

    if len(int_list) != 4:
        raise ValueError(
            "Parameter 'int_list' must be list with four unsigned int numbers!"
        )

    # endianness
    endianness = ">" if big_endian else "<"

    # convert to the byte string
    byte_str = struct.pack(f"{endianness}HHHH", *int_list)

    # unpack byte string to double
    return struct.unpack(f"{endianness}Q", byte_str)[0]
