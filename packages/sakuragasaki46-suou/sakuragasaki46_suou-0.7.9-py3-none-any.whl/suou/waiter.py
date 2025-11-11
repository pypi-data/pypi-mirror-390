"""
Content serving API over HTTP, based on Starlette.

NEW 0.6.0

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

import warnings
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

from suou.functools import future

@future()
class Waiter():
    def __init__(self):
        self.routes: list[Route] = []
        self.production = False

    def _build_app(self) -> Starlette:
        return Starlette(
            debug = not self.production,
            routes= self.routes
        )

    ## TODO get, post, etc.

def ok(content = None, **ka):
    if content is None:
        return Response(status_code=204, **ka)
    elif isinstance(content, dict):
        return JSONResponse(content, **ka)
    elif isinstance(content, str):
        return PlainTextResponse(content, **ka)
    return content

def ko(status: int, /, content = None, **ka):
    if status < 400 or status > 599:
        warnings.warn(f'HTTP {status} is not an error status', UserWarning)
    if content is None:
        return Response(status_code=status, **ka)
    elif isinstance(content, dict):
        return JSONResponse(content, status_code=status, **ka)
    elif isinstance(content, str):
        return PlainTextResponse(content, status_code=status, **ka)
    return content

# This module is experimental and therefore not re-exported into __init__
__all__ = ('ko', 'ok', 'Waiter')