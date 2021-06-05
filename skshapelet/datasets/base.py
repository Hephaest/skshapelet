import os
import tempfile
import zipfile
import shutil

from urllib.request import urlretrieve
from sktime.utils.data_io import load_from_tsfile_to_dataframe
from sklearn.utils.multiclass import class_distribution

import pandas as pd
import numpy as np

NonExistentKey = -1

DIRNAME = "database"
MODULE = os.path.dirname(__file__)

def get_dist_key(dist, value):
    """A static method to return the key that stored the required value or return -1 if not exist.

    Args:
        dist: dist
            A dist that may contain some key-value pairs.
        value: string
            The class label.

    Returns:
        output: int
            The integer that stored the associated with the value or returns -1 if not exist.
    """
    for key, val in dist.items():
        if value == val:
            return key
    return NonExistentKey


def pre_processing(y, dist=None):
    """A static method to pre-process the y.

    Args:
        y: string
            A string that may contain characters or integer.
        dist: dist_like, optional
            A dist that may contain some key-value pairs.

    Returns:
        output: ndarray, dist
            The numpy array and a dist that have been processed.
    """
    distinct_label = class_distribution(np.asarray(y).reshape(-1, 1))[0][0]
    labels = [idx for idx in range(0, len(distinct_label))]
    transform_y = []
    if dist is None:
        dist = {}
        for idx in range(0, len(y)):
            label = y[idx]
            key = get_dist_key(dist, label)

            if key is NonExistentKey:
                key = labels.pop(0)
                dist[key] = label

            transform_y.append(key)
    else:
        for idx in range(0, len(y)):
            label = y[idx]
            key = get_dist_key(dist, label)
            transform_y.append(key)

    return np.asarray(transform_y), dist


def load_dataset(name, split, return_X_y, dist=None):
    """A static method to load dataset by name.
    This mirrors the sktime implementation.

    Args:
        name: string
            The name of dataset.
        split: string
            Whether it belongs to the train or test set or none of them.
        return_X_y: bool
            Whether should return true or false.
        dist: dist, optional
            A dist that may contain some key-value pairs.

    Returns:
        output: ndarray, ndarray, dist
    """
    extract_path = os.path.join(MODULE, DIRNAME)
    local_module = MODULE
    local_dirname = DIRNAME

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    if name not in _list_downloaded_datasets(extract_path):
        url = "http://timeseriesclassification.com/Downloads/%s.zip" % name
        # This also tests the validitiy of the URL, can't rely on the html
        # status code as it always returns 200
        try:
            _download_and_extract(url, extract_path)
        except zipfile.BadZipFile as e:
            raise ValueError(
                "Invalid dataset name. Please make sure the dataset is "
                "available on http://timeseriesclassification.com/."
            ) from e

    if split in ("train", "test"):
        fname = name + "_" + split.upper() + ".ts"
        abspath = os.path.join(local_module, local_dirname, name, fname)
        X, y = load_from_tsfile_to_dataframe(abspath)
        if y is float or y is int:
            y = [int(label) for label in y]
        else:
            y, dist = pre_processing(y, dist)
        if np.amin(y) > 0:
            y = y - 1
    else:
        raise ValueError("Invalid `split` value")

    # Return appropriately
    if return_X_y:
        return X, y, dist
    else:
        X["class_val"] = pd.Series(y)
        return X, dist


def _list_downloaded_datasets(extract_path):
    """
    Returns a list of all the currently downloaded datasets.
    This mirrors the sktime implementation.

    Args:
        extract_path: string
            The specific extract path.

    Returns:
        datasets : list
            List of the names of datasets downloaded.
    """
    if extract_path is None:
        data_dir = os.path.join(MODULE, DIRNAME)
    else:
        data_dir = extract_path
    datasets = [
        path
        for path in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, path))
    ]
    return datasets


def _download_and_extract(url, extract_path=None):
    """Helper function for downloading and unzipping datasets
    This mirrors the sktime implementation.

    Args:
        url : string
            Url pointing to file to download
        extract_path : string, optional (default: None)
            path to extract downloaded zip to, None defaults
            to sktime/datasets/data

    Returns:
        extract_path : string or None
            if successful, string containing the path of the extracted file, None
            if it wasn't succesful.
    """
    file_name = os.path.basename(url)
    dl_dir = tempfile.mkdtemp()
    zip_file_name = os.path.join(dl_dir, file_name)
    urlretrieve(url, zip_file_name)

    if extract_path is None:
        extract_path = os.path.join(MODULE, DIRNAME + "/%s/" % file_name.split(".")[0])
    else:
        extract_path = os.path.join(extract_path, "%s/" % file_name.split(".")[0])

    try:
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
        zipfile.ZipFile(zip_file_name, "r").extractall(extract_path)
        shutil.rmtree(dl_dir)
        return extract_path
    except zipfile.BadZipFile:
        shutil.rmtree(dl_dir)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        raise zipfile.BadZipFile(
            "Could not unzip dataset. Please make sure the URL is valid."
        )