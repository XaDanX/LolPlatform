import functools
import struct
from typing import Any

import pymem
import asyncio

"""

Made by StarrFox

"""
type_format_dict = {
    "char": "<c",
    "signed char": "<b",
    "unsigned char": "<B",
    "bool": "?",
    "short": "<h",
    "unsigned short": "<H",
    "int": "<i",
    "unsigned int": "<I",
    "long": "<l",
    "unsigned long": "<L",
    "long long": "<q",
    "unsigned long long": "<Q",
    "float": "<f",
    "double": "<d",
}


class Memory:

    process: pymem.Pymem

    @staticmethod
    async def run_in_executor(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        function = functools.partial(func, *args, **kwargs)

        return await loop.run_in_executor(None, function)

    async def read_bytes(self, address: int, size: int) -> bytes:

        return await self.run_in_executor(self.process.read_bytes, address, size)

    async def write_bytes(self, address: int, value: bytes):

        size = len(value)
        await self.run_in_executor(
            self.process.write_bytes,
            address,
            value,
            size,
        )

    async def read(self, address: int, data_type: str) -> Any:
        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} invalid data type")

        data = await self.read_bytes(address, struct.calcsize(type_format))
        return struct.unpack(type_format, data)[0]

    async def write(self, address: int, value: Any, data_type: str):

        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} invalid data type")

        packed_data = struct.pack(type_format, value)
        await self.write_bytes(address, packed_data)

    async def read_string(self, address: int, length: int) -> Any:
        data = await self.run_in_executor(self.process.read_string, address, length)
        return data
