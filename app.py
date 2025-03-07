from aiohttp import web
from routes import list_datasets, serve_static
from websocket_handler import websocket_handler

async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/ws', websocket_handler),
        web.get('/datasets', list_datasets),
        web.get('/static/{path:.*}', serve_static)  # Serve static files from the /static path
    ])
    app.router.add_get('/{path:.*}', serve_static)  # Catch-all route for unmatched routes
    return app
