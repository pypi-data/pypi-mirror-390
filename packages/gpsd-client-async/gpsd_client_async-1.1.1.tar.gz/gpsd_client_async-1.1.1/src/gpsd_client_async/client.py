import asyncio
from typing import Union

from . import messages

POLL = "?POLL;\r\n"
WATCH = "?WATCH={}\r\n"


class GpsdClient:
    devices: messages.Devices
    watch: messages.Watch
    version: messages.Version

    _host: str
    _port: int
    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter

    def __init__(self, host: str = "127.0.0.1", port: int = 2947, watch_config: messages.Watch=messages.Watch()):
        self._host = host
        self._port = port
        self.watch_config = watch_config

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)

        self._writer.write(WATCH.format(self.watch_config.model_dump_json(by_alias=True, exclude={"class_"})).encode())
        await self._writer.drain()

        self.version = await self.get_result()
        self.devices = await self.get_result()
        self.watch = await self.get_result()

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()

    async def get_result(self) -> messages.AnyGPSDMessage:
        return messages.parse(await self._reader.readline())

    async def poll(self) -> messages.AnyGPSDMessage:
        self._writer.write(POLL.encode())
        await self._writer.drain()
        return await self.get_result()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self) -> Union[messages.TPV, messages.Sky]:
        msg = await self.get_result()
        while not isinstance(msg , (messages.TPV, messages.Sky)):  # can be Poll message
            msg = await self.get_result()
        return msg
