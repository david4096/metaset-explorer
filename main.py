import asyncio
from aiohttp import web
from app import init_app
import logging

if __name__ == "__main__":
    logging.info("Starting server")
    app = asyncio.run(init_app())
    web.run_app(app, port=8080)
