"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""
from http import HTTPStatus

from aiohttp import web
from botbuilder.core.integration import aiohttp_error_middleware

from bots import bot

routes = web.RouteTableDef()

@routes.post("/api/messages")
async def on_messages(req: web.Request) -> web.Response:
    res = await bot.app.process(req)

    if res is not None:
        return res
    return web.Response(status=HTTPStatus.OK)

bot_app = web.Application(middlewares=[aiohttp_error_middleware])
bot_app.add_routes(routes)

from config import Config

if __name__ == "__main__":
    web.run_app(bot_app, host="localhost", port=Config.PORT)