import asyncio
import json
import pandas as pd
import logging
from aiohttp import web
import os
import math
import gzip
import base64

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Load datasets (assumed to be stored in Parquet format)
def load_datasets():
    logger.info("Loading datasets from Parquet file")
    data = pd.read_parquet('hfdatasets4.parquet')
    logger.info("Datasets loaded successfully")
    logger.info(f"Data shape: {data.shape}")
    return data


# Handle WebSocket connections
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info("WebSocket connection established")
    data = load_datasets()

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                request_data = json.loads(msg.data)
                if request_data["type"] == "start_stream":
                    dataset_name = request_data.get("dataset_name")
                    batch_size = request_data.get("batch_size", 100)  # Default batch size
                    logger.info(f"Starting stream for dataset: {dataset_name} with batch size: {batch_size}")
                    await start_stream(ws, data, dataset_name, batch_size)
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WebSocket connection closed with exception {ws.exception()}")
    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}")
    finally:
        logger.info("WebSocket connection closed")

    return ws


async def start_stream(ws, data, dataset_name, batch_size):
    # Filter data for the requested dataset
    dataset_points = data[data['dataset_name'] == dataset_name]
    if dataset_points.empty:
        logger.warning(f"Dataset not found: {dataset_name}")
        await ws.send_json({"error": "Dataset not found"})
        await ws.close()
        return

    logger.info(f"Streaming {len(dataset_points)} points for dataset: {dataset_name}")

    # Stream data in batches
    total_points = len(dataset_points)
    total_batches = math.ceil(total_points / batch_size)

    for i in range(total_batches):
        batch_start = i * batch_size
        batch_end = batch_start + batch_size
        batch = dataset_points.iloc[batch_start:batch_end]

        # Convert batch to JSON-friendly format
        batch_data = batch.to_dict(orient='records')
        json_data = json.dumps({"type": "data_batch", "data": batch_data})

        # Compress data
        compressed_data = gzip.compress(json_data.encode('ascii'))
        # Encode as base64 to ensure binary-safe transmission
        encoded_data = base64.b64encode(compressed_data).decode('ascii')

        await ws.send_str(encoded_data)

    # Send end of stream message
    await ws.send_json({"type": "end_of_stream"})
    logger.info("End of stream reached")
    await ws.close()


# Endpoint to list dataset names
async def list_datasets(request):
    logger.info("Listing datasets")
    data = load_datasets()
    datasets = data['dataset_name'].unique().tolist()
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


async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/ws', websocket_handler),
        web.get('/datasets', list_datasets),
        web.get('/static/{path:.*}', serve_static)  # Serve static files from the /static path
    ])
    app.router.add_get('/{path:.*}', serve_static)  # Catch-all route for unmatched routes
    return app


# Main entry point
if __name__ == "__main__":
    logger.info("Starting server")
    app = asyncio.run(init_app())
    web.run_app(app, port=8080)
