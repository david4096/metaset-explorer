import asyncio
import json
import gzip
import base64
import math
from aiohttp import web
from data_loader import lazy_load_dataset
from config import logger
import os


# Assume dataset_name corresponds to a filename
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info("WebSocket connection established")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                request_data = json.loads(msg.data)
                if request_data["type"] == "start_stream":
                    dataset_name = request_data.get("dataset_name")
                    batch_size = request_data.get("batch_size", 100)  # Default batch size

                    file_name = f"{dataset_name}.parquet"
                    loader = lazy_load_dataset(file_name)

                    if not os.path.isfile(os.path.join('data', file_name)):
                        logger.warning(f"Dataset file not found: {file_name}")
                        await ws.send_json({"error": "Dataset file not found"})
                        await ws.close()
                        return

                    logger.info(f"Starting stream for dataset: {dataset_name} with batch size: {batch_size}")
                    data = loader()
                    await start_stream(ws, data, batch_size)
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WebSocket connection closed with exception {ws.exception()}")
    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}")
    finally:
        logger.info("WebSocket connection closed")

    return ws


async def start_stream(ws, data, batch_size):
    # Stream data in batches
    total_points = len(data)
    total_batches = math.ceil(total_points / batch_size)

    for i in range(total_batches):
        batch_start = i * batch_size
        batch_end = batch_start + batch_size
        batch = data.iloc[batch_start:batch_end]

        # Convert batch to JSON-friendly format
        batch_data = batch.to_dict(orient='records')
        json_data = json.dumps({"type": "data_batch", "data": batch_data})

        # Compress data
        #compressed_data = gzip.compress(json_data.encode('ascii'))
        # Encode as base64 to ensure binary-safe transmission
        #encoded_data = base64.b64encode(compressed_data).decode('ascii')

        await ws.send_str(json_data)

    # Send end of stream message
    await ws.send_json({"type": "end_of_stream"})
    logger.info("End of stream reached")
    await ws.close()
