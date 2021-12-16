from __future__ import annotations

import logging

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.params import Depends, Header

from aioprometheus import REGISTRY, render
from starlette.responses import Response

import collectors

log: logging.Logger = logging.getLogger("onos-prometheus")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

app = FastAPI()


async def perform_collection():
    pass


@app.get("/metrics")
async def handle_metrics(response: Response, accept: list[str] = Header(None)):
    await collectors.perform()

    content, http_headers = render(REGISTRY, accept)
    return Response(content=content, media_type=http_headers["Content-Type"])
