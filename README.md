# Metaset Explorer

Metaset Explorer is a web-based application for visualizing datasets in 3D space. The backend, written in Python, serves data from a Parquet file and supports WebSocket connections for efficient data streaming. The frontend, built with Three.js, allows users to interact with and explore the data visually.

<img width="1083" alt="Screenshot 2024-08-06 at 1 19 22 AM" src="https://github.com/user-attachments/assets/381b657a-c119-41b8-a43c-22e287bdf545">



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
   python dummy_metaset.py
   ```

3. Run the server:

   ```bash
   python main.py
   ```


## Usage

1. Open `http://localhost:8080` in a web browser.
2. Select a dataset to visualize.
3. Use the controls to explore the data.

## License

Licensed under the MIT License.
