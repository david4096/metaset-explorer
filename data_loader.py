import pandas as pd
import os
from config import logger

# Directory where Parquet files are stored
PARQUET_DIR = 'data/'

import os
from config import logger

# Directory where Parquet files are stored
PARQUET_DIR = 'data/'


def get_parquet_files():
    """List all Parquet files in the data directory."""
    try:
        if not os.path.isdir(PARQUET_DIR):
            raise FileNotFoundError(f"Directory not found: {PARQUET_DIR}")

        files = [f for f in os.listdir(PARQUET_DIR) if f.endswith('.parquet')]
        logger.info(f"Found Parquet files: {files}")
        return files
    except Exception as e:
        logger.error(f"Error listing Parquet files: {e}")
        raise


def lazy_load_dataset(file_name):
    """Create a lazy loader for the specified Parquet file."""
    file_path = os.path.join(PARQUET_DIR, file_name)
    logger.info(f"Preparing to load dataset from {file_path}")

    # Return a lazy loader function
    def load():
        logger.info(f"Loading dataset from {file_path}")
        return pd.read_parquet(file_path)

    return load
