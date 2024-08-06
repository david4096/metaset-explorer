# Metaset Explorer

Metaset Explorer is a web-based application for visualizing datasets in 3D space. The backend, written in Python, serves data from a Parquet file and supports WebSocket connections for efficient data streaming. The frontend, built with Three.js, allows users to interact with and explore the data visually.

## Features

- **3D Visualization** of datasets.
- **Interactive Controls** for navigating the 3D space.
- **WebSocket Streaming** for efficient data transfer.

## Setup

### Requirements

- Python 3.10+
- Node.js
- Python packages: `websockets`, `pyarrow`, `numpy`, `pandas`
- JavaScript packages: `three`, `pako`

### Installation

1. Clone the repository and navigate to the project directory.
2. Set up the Python environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   pip install -r requirements.txt
   ```

2. Generate test data:

   ```bash
   python test_data_generator.py
   ```

3. Run the server:

   ```bash
   python server.py
   ```


## Usage

1. Open `http://localhost:8080` in a web browser.
2. Select a dataset to visualize.
3. Use the controls to explore the data.

## License

Licensed under the MIT License.
