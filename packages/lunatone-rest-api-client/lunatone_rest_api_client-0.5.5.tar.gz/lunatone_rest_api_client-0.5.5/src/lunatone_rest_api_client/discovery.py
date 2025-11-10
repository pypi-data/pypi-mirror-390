"""Discovery module for Lunatone interfaces."""

import asyncio
from dataclasses import dataclass
from enum import StrEnum
import json
import socket
from typing import Any, Final, AsyncGenerator

DISCOVERY_ADDRESS: Final[str] = "255.255.255.255"
DISCOVERY_PORT: Final[int] = 5555
DISCOVERY_MESSAGE: Final[str] = "discovery"
DISCOVERY_LISTEN_TIMEOUT_SECONDS: Final[float] = 3.0


class LunatoneDiscoveryTypes(StrEnum):
    """DiscoveryTypes."""

    DALI2_IOT = "dali-2-iot"
    DALI2_IOT4 = "dali-2-iot4"
    DALI2_DISPLAY = "dali-2-display"


@dataclass
class LunatoneDiscoveryInfo:
    """LunatoneDiscoveryInfo."""

    host: str
    name: str
    type: LunatoneDiscoveryTypes


class LunatoneUDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol implementation for discovering Lunatone interfaces."""

    def __init__(self, queue: asyncio.Queue) -> None:
        """Initialize the UDP protocol instance."""
        super().__init__()
        self._queue: asyncio.Queue[LunatoneDiscoveryInfo] = queue

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        """Handle an incoming UDP datagram."""
        try:
            message = json.loads(data.decode())
        except json.JSONDecodeError:
            return
        if not ("type" in message and "name" in message):  # Validate message
            return
        if message["type"] in LunatoneDiscoveryTypes:
            info = LunatoneDiscoveryInfo(addr[0], message["name"], message["type"])
            self._queue.put_nowait(info)


async def async_discover_devices_stream(
    loop: asyncio.AbstractEventLoop,
    timeout: float = DISCOVERY_LISTEN_TIMEOUT_SECONDS,
    local_ip: str = "0.0.0.0",
) -> AsyncGenerator[LunatoneDiscoveryInfo, None]:
    """Yield devices one by one as they arrive (streaming style)."""
    queue: asyncio.Queue[LunatoneDiscoveryInfo] = asyncio.Queue()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: LunatoneUDPProtocol(queue),
        local_addr=(local_ip, DISCOVERY_PORT),
        family=socket.AF_INET,
        allow_broadcast=True,
    )
    try:
        transport.sendto(DISCOVERY_MESSAGE.encode(), (DISCOVERY_ADDRESS, DISCOVERY_PORT))
        end = loop.time() + timeout
        while loop.time() < end:
            try:
                device = await asyncio.wait_for(queue.get(), timeout=end - loop.time())
                yield device
            except asyncio.TimeoutError:
                break
    finally:
        transport.close()


async def async_discover_devices(
    loop: asyncio.AbstractEventLoop,
    timeout: float = DISCOVERY_LISTEN_TIMEOUT_SECONDS,
    local_ip: str = "0.0.0.0",
) -> list[LunatoneDiscoveryInfo]:
    """Collect all devices and return them at once (batch style)."""
    devices: list[LunatoneDiscoveryInfo] = []
    async for dev in async_discover_devices_stream(loop, timeout, local_ip):
        devices.append(dev)
    return devices
