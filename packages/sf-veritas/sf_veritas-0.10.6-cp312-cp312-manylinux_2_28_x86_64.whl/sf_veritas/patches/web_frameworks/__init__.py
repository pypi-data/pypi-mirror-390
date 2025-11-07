from typing import List, Optional

from .aiohttp import patch_aiohttp
from .async_websocket_consumer import patch_async_consumer_call
from .blacksheep import patch_blacksheep
from .bottle import patch_bottle
from .cherrypy import patch_cherrypy
from .django import find_and_modify_output_wrapper, patch_django_middleware
from .eve import patch_eve
from .falcon import patch_falcon
from .fastapi import patch_fastapi
from .flask import patch_flask
from .klein import patch_klein
from .litestar import patch_litestar
from .pyramid import patch_pyramid
from .quart import patch_quart

# Robyn is NOT SUPPORTED - see ROBYN_LIMITATION.md
# from .robyn import patch_robyn
# Sanic is NOT SUPPORTED - see SANIC_LIMITATION.md
# from .sanic import patch_sanic
from .starlette import patch_starlette
from .strawberry import patch_strawberry
from .tornado import patch_tornado


def patch_web_frameworks(routes_to_skip: Optional[List[str]] = None):
    routes_to_skip = routes_to_skip or []

    patch_strawberry()
    patch_async_consumer_call()
    find_and_modify_output_wrapper()
    patch_django_middleware(routes_to_skip)
    patch_fastapi(routes_to_skip)
    patch_flask(routes_to_skip)
    patch_falcon(routes_to_skip)
    patch_bottle(routes_to_skip)
    patch_quart(routes_to_skip)
    patch_tornado(routes_to_skip)
    patch_aiohttp(routes_to_skip)
    patch_blacksheep(routes_to_skip)
    patch_cherrypy(routes_to_skip)
    patch_pyramid(routes_to_skip)
    patch_litestar(routes_to_skip)
    patch_klein(routes_to_skip)
    patch_eve(routes_to_skip)
    # Sanic is NOT SUPPORTED - see SANIC_LIMITATION.md
    # patch_sanic(routes_to_skip)
    patch_starlette(routes_to_skip)
    # Robyn is NOT SUPPORTED - see ROBYN_LIMITATION.md
    # patch_robyn(routes_to_skip)


__all__ = ["patch_web_frameworks"]
