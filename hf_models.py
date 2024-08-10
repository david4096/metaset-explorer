import argparse
import builtins
import json
import numpy as np
import pandas as pd
from huggingface_hub import HfApi
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
import umap


def get_non_builtin_attributes(obj):
    # Get a list of all attributes (including built-ins) of the object
    all_attrs = dir(obj)
    # Filter out attributes that are in the built-ins module
    non_builtin_attrs = [attr for attr in all_attrs if not hasattr(builtins, attr) and attr[:2] != '__']
    return non_builtin_attrs


def ds_dict(ds, attrs):
    ret = {}
    for attr in attrs:
        ret[attr] = getattr(ds, attr, "")
    ret['id'] = ds.id
    return ret


def clean_dates(lds):
    for d in lds:
        d['created_at'] = str(d['created_at'])
        d['lastModified'] = str(d['created_at'])
        d['last_modified'] = str(d['created_at'])
    return lds


def generate_datasets(filename, num_results, num_clusters):
    api = HfApi()
    hfdatasets = api.list_models(limit=num_results)
    dss = list(hfdatasets)

    attrs = get_non_builtin_attributes(dss[0])
    dssdicts = list(map(lambda ds: ds_dict(ds, attrs), dss))
    cleandss = clean_dates(dssdicts)

    vec = DictVectorizer()
    embedded = vec.fit_transform(cleandss)

    imp = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=None)
    imp.fit(embedded)
    imputed = imp.transform(embedded)

    mapper = umap.UMAP(metric='cosine', low_memory=True, n_components=3)
    umapped = mapper.fit_transform(imputed)

    clustering_model = KMeans(n_clusters=num_clusters)
    clusters = clustering_model.fit(umapped).labels_

    labeled = [[x[0], x[1], x[2], c, d] for x, d, c in zip(umapped, dssdicts, clusters)]

    data = {
        'point_id': [],
        'x': [],
        'y': [],
        'z': [],
        'w': [],
        'additional_info': []
    }

    dataset_name = "hfdataset"
    for u, point_id in zip(labeled, range(len(labeled))):
        data['point_id'].append(u[4]['_id'])
        data['x'].append(u[0])
        data['y'].append(u[1])
        data['z'].append(u[2])
        data['w'].append(u[3])
        data['additional_info'].append(json.dumps(u[4]))


    df = pd.DataFrame(data)
    df.to_parquet(filename)


def main():
    parser = argparse.ArgumentParser(description="Generate a dataset of the metadata about models from Hugging Face.")
    parser.add_argument('filename', type=str, help='Output Parquet filename')
    parser.add_argument('--num-results', type=int, default=300, help='Number of results to fetch from Hugging Face')
    parser.add_argument('--num-clusters', type=int, default=20, help='Number of clusters for the clustering model')

    args = parser.parse_args()

    generate_datasets(args.filename, args.num_results, args.num_clusters)


if __name__ == "__main__":
    main()
