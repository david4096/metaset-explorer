import os
from aiohttp import web
from data_loader import get_parquet_files
from websocket_handler import websocket_handler
from config import logger

# Endpoint to list dataset names
async def list_datasets(request):
    logger.info("Listing datasets")
    files = get_parquet_files()
    datasets = [f.replace('.parquet', '') for f in files]
    return web.json_response(datasets)

# Serve static HTML files
async def serve_static(request):
    path = request.match_info.get('path', 'index.html')
    file_path = os.path.join('static', path)

    if os.path.isfile(file_path):
        logger.info(f"Serving static file: {path}")
        return web.FileResponse(file_path)
    else:
        logger.info(f"File not found: {path}, serving index.html")
        return web.FileResponse('static/index.html')
