from __future__ import annotations

from typing import cast

import httpx
from aioprometheus import REGISTRY, Gauge
from utils import CamelcaseBaseModel, get_settings
from yarl import URL


class FlowStats(CamelcaseBaseModel):
    device: str
    active_entries: int

    def push_counters(self):
        field = "active_flow_entries"

        if field in REGISTRY.collectors:
            c = cast(Gauge, REGISTRY.get(field))
        else:
            c = Gauge(field, field)
        c.set({"device": self.device}, self.active_entries)


class Statistics(CamelcaseBaseModel):
    statistics: list[FlowStats]

    def push_counters(self):
        for device in self.statistics:
            device.push_counters()


settings = get_settings()

url = URL(settings.onos_api_url) / "statistics" / "flows" / "activeentries"


async def perform():
    async with httpx.AsyncClient() as client:
        resp = await client.get(str(url), auth=(settings.onos_user, settings.onos_pass))
        resp.raise_for_status()

    stats = Statistics.parse_obj(resp.json())
    stats.push_counters()
