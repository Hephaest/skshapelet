import numpy as np
import pandas as pd

from sktime.utils.data_processing import from_nested_to_3d_numpy
from sktime.utils.data_processing import is_nested_dataframe
from sklearn.utils.validation import check_consistent_length

X_TYPES = (pd.DataFrame, np.ndarray)
Y_TYPES = (pd.Series, np.ndarray)


def check_transform_series(X_list, y):
    """Returns X, y that have been transformed into numpy arrays.
    This mirrors the sktime implementation.

    Args:
        X_list: pandas DataFrame
            The array is presented by pandas.
        y: pandas DataFrame
            The array is presented by pandas.

    Returns:
        output: ndarray, ndarray
            The array is presented by numpy.
    """
    y = check_transform_y(y)
    check_consistent_length(X_list, y)

    X = check_transform_X(X_list)
    return X, y


def check_transform_X(X_list):
    """Returns X that has been transformed into numpy arrays.
    This mirrors the sktime implementation.

    Args:
        X_list: pandas DataFrame
            The array is presented by pandas.

    Returns:
        X_list: ndarray
            The array is presented by numpy.
    """
    if not isinstance(X_list, X_TYPES):
        raise TypeError(f"Array must be np.ndarray or pd.DataFrame type.")

    # check input type
    if isinstance(X_list, np.ndarray):
        if not X_list.ndim == 3:
            raise TypeError(f"X must be a 3D array")

    # enforce minimum number of columns
    n_columns = X_list.shape[1]
    if n_columns == 0:
        raise ValueError(f"Array should have at least 1 column")

    # enforce minimum number of instances
    check_min_instances(X_list)

    # check pd.DataFrame
    if isinstance(X_list, pd.DataFrame):
        if not is_nested_dataframe(X_list):
            raise ValueError(
                "If passed as a pd.DataFrame, X must be a nested "
                "pd.DataFrame, with pd.Series or np.arrays inside cells."
            )
        # convert pd.DataFrame
        X_list = from_nested_to_3d_numpy(X_list)

    return X_list


def check_transform_y(y):
    """Returns y that has been transformed into numpy arrays.

    Args:
        y: pandas DataFrame
            The array is presented by pandas.

    Returns:
        y: ndarray
            The array is presented by numpy.
    """
    if not isinstance(y, Y_TYPES):
        raise TypeError(f"Array must be np.ndarray or pd.Series type.")
    check_min_instances(y)

    return y.to_numpy() if isinstance(y, pd.Series) else y


def check_min_instances(arr):
    """Check the array has a suitable size.

    Args:
        arr: pandas DataFrame
            The array that needs to be tested.

    Returns:
        output: bool
            The instance length requirement check result.
    """
    n_instances = arr.shape[0]
    if n_instances == 0:
        raise ValueError(f"Array should have at least 1 instance")


def check_min_length(require_len, actual_len):
    """Check the instance has a suitable size.

    Args:
        require_len: int
            The required instance length.
        actual_len: int
            The real instance length.

    Returns:
        output: int
            The minimum length of the instance.
    """
    if require_len > 0:
        return min(require_len, actual_len)
    else:
        return actual_len