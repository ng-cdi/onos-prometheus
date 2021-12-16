from collectors import port_statistics, flow_entries


async def perform():
    await port_statistics.perform()
    await flow_entries.perform()
