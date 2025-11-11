# Asycio GPSd Client

Fork of very well done asyncio-gpsd-client that was unfortunately quite out of date.
I just cleaned it up a bit and updated dependencies.

GPSd is an unified interface to GNSS modules in Linux. GPSd publishes its data on localhost:2367.
Upon connection, it sends initial data (Devices, Watch, Version messages) that are available in
GpsdClient instance. The client then provides an async iterator that reports the runtime messages
TPV (location update) and Sky (status update). For details about messages, refer to `messages.py`.

# Install

```shell
pip install gpsd-client-async
```

# Usage

```python
import asyncio

import gpsd_client_async as gpsd

async def main():
    async with gpsd.GpsdClient() as client:
        async for message in client:
            print(message)  # TPV or Sky message

asyncio.run(main())
```

## Debugging

The client reports messages to `"agpsd"` logger.