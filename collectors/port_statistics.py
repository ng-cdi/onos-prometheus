from __future__ import annotations

from typing import cast

import httpx
from aioprometheus import REGISTRY, Counter
from utils import CamelcaseBaseModel, get_settings
from yarl import URL


class PortStats(CamelcaseBaseModel):
    port: int
    packets_received: int
    packets_sent: int
    bytes_received: int
    bytes_sent: int
    packets_rx_dropped: int
    packets_tx_dropped: int
    packets_rx_errors: int
    packets_tx_errors: int
    duration_sec: int

    def push_counters(self, device: str):
        fields = [
            ("packets_received", "packets_received", self.packets_received),
            ("packets_sent", "packets_sent", self.packets_sent),
            ("bytes_received", "bytes_received", self.bytes_received),
            ("bytes_sent", "bytes_sent", self.bytes_sent),
            ("packets_rx_dropped", "packets_rx_dropped", self.packets_rx_dropped),
            ("packets_tx_dropped", "packets_tx_dropped", self.packets_tx_dropped),
            ("packets_rx_errors", "packets_rx_errors", self.packets_rx_errors),
            ("packets_tx_errors", "packets_tx_errors", self.packets_tx_errors),
        ]

        for field, desc, val in fields:
            if field in REGISTRY.collectors:
                c = cast(Counter, REGISTRY.get(field))
            else:
                c = Counter(field, desc)
            c.set({"device": device, "port": str(self.port)}, val)


class DeviceStats(CamelcaseBaseModel):
    device: str
    ports: list[PortStats]

    def push_counters(self):
        for port in self.ports:
            port.push_counters(self.device)


class Statistics(CamelcaseBaseModel):
    statistics: list[DeviceStats]

    def push_counters(self):
        for device in self.statistics:
            device.push_counters()


settings = get_settings()

url = URL(settings.onos_api_url) / "statistics" / "ports"


async def perform():
    async with httpx.AsyncClient() as client:
        resp = await client.get(str(url), auth=(settings.onos_user, settings.onos_pass))
        resp.raise_for_status()

    stats = Statistics.parse_obj(resp.json())
    stats.push_counters()
