import builtins
from huggingface_hub import HfApi
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer
import numpy as np
import umap
import pandas as pd
import json


api = HfApi()
hfdatasets = api.list_datasets(limit=300000)
dss = list(hfdatasets)

def get_non_builtin_attributes(obj):
    # Get a list of all attributes (including built-ins) of the object
    all_attrs = dir(obj)
    # Filter out attributes that are in the built-ins module
    non_builtin_attrs = [attr for attr in all_attrs if not hasattr(builtins, attr) and attr[:2] != '__']
    return non_builtin_attrs

attrs = get_non_builtin_attributes(dss[0])
def ds_dict(ds):
  ret = {}
  for attr in attrs:
    ret[attr] = getattr(ds, attr, "")
  ret['id'] = ds.id
  return ret

dssdicts = list(map(ds_dict, dss))

def clean_dates(lds):
  for d in lds:
    d['created_at'] = str(d['created_at'])
    d['lastModified'] = str(d['created_at'])
    d['last_modified'] = str(d['created_at'])
  return lds

cleandss = clean_dates(dssdicts)

vec = DictVectorizer()
embedded = vec.fit_transform(cleandss)

imp = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=None)
# fit the imputer - suppose missing data is in the 0th column
imp.fit(embedded)
# transform the data
imputed = imp.transform(embedded)

mapper = umap.UMAP(metric='cosine', low_memory=True, n_components=3)
umapped = mapper.fit_transform(imputed)

labeled = [[x[0], x[1], x[2], d] for x, d in zip(umapped, dssdicts)]

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
dataset_name = f"hfdataset"
for u, d, point_id in zip(umapped, dssdicts, range(len(dss))):
    data['dataset_name'].append(dataset_name)
    data['point_id'].append(d['_id'])
    data['x'].append(u[0])
    data['y'].append(u[1])
    data['z'].append(u[2])
    data['w'].append(u[2])
    data['additional_info'].append(json.dumps(d))

df = pd.DataFrame(data)
df.to_parquet('hfdatasets4.parquet')
