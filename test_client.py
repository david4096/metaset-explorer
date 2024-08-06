import asyncio
import websockets
import json
import requests
import random


# Fetch the list of datasets from the server
async def fetch_datasets():
    uri = "http://localhost:8080/datasets"  # HTTP URL for listing datasets
    response = requests.get(uri)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch datasets")
        return []


# Fetch and stream data for a given dataset
async def fetch_dataset(dataset_name):
    uri = "ws://localhost:8080/ws"  # WebSocket URL for streaming data
    async with websockets.connect(uri) as websocket:
        # Send request to start the data stream
        request = {
            "type": "start_stream",
            "dataset_name": dataset_name
        }
        await websocket.send(json.dumps(request))
        print(f"Requested dataset: {dataset_name}")

        # Receive data stream
        try:
            async for message in websocket:
                point = json.loads(message)

                if point.get("type") == "end_of_stream":
                    print("End of stream reached.")
                    break
                elif "error" in point:
                    print(f"Error received: {point['error']}")
                    break
                else:
                    print(f"Received point: {point}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
        finally:
            print("WebSocket connection closed")


# Main entry point
async def main():
    # List datasets
    datasets = await fetch_datasets()
    if datasets:
        # Choose a random dataset name
        dataset_name = random.choice(datasets)
        print(f"Randomly selected dataset: {dataset_name}")

        # Fetch and print the dataset
        await fetch_dataset(dataset_name)
    else:
        print("No datasets available.")


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
