import pandas as pd
import numpy as np

# Define the number of datasets and points per dataset
num_datasets = 100
points_per_dataset = 5000

# Generate data
data = {
    'dataset_name': [],
    'point_id': [],
    'x': [],
    'y': [],
    'z': [],
    'w': [],
    'additional_info': []
}

# Populate the data dictionary
for dataset_id in range(num_datasets):
    dataset_name = f"Dataset_{dataset_id}"
    for point_id in range(points_per_dataset):
        data['dataset_name'].append(dataset_name)
        data['point_id'].append(point_id)
        data['x'].append(np.random.rand())
        data['y'].append(np.random.rand())
        data['z'].append(np.random.rand())
        data['w'].append(np.random.rand())
        data['additional_info'].append(f"Metadata for point {point_id} in {dataset_name}")

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a Parquet file
df.to_parquet('test_metaset.parquet')

print("Test MetaSet Parquet file generated successfully.")
