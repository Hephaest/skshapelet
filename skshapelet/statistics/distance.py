import numpy as np


def zscore(a, axis=0, ddof=0):
    """Calculate the z-score of 1-D array.

    Args:
        a: ndarray
            The required array.
        axis: int, optional
            The axis of the array.
        ddof: int, optional
            Means Delta Degrees of Freedom.

    Returns:
        output: ndarray
            The z-scores, standardized by mean and standard deviation of input array a.
    """
    a = np.asanyarray(a)

    if a.size == 0:
        return np.empty(a.shape)

    std = a.std(axis=axis, ddof=ddof, keepdims=True)

    if std == 0:
        return np.empty(a.shape)

    mn = a.mean(axis=axis, keepdims=True)
    return (a - mn) / std


def euclidean_distance(this, other):
    """Calculate the Euclidean distance between 2 1-D arrays.

    Args:
        this: ndarray
            The array.
        other: ndarray
            The comparative array.

    Returns:
        output: float
            The square of Euclidean distance.
    """
    dist_norm = np.linalg.norm(this - other)
    return dist_norm ** 2


def mahalanobis_distance(X, mean, inv_cov):
    """Calculate the Mahalanobis distance between 2 1-D arrays.

    Args:
        X: ndarray
            The comparative array.
        mean: float
            The mean of the array.
        inv_cov:
            Inverse covariance matrix related to the array.

    Returns:
        output: float
            The square of Mahalanobis distance.
    """
    residual = X - mean
    transpose_residual = np.transpose(residual)
    dist_square = np.dot(
        np.dot(residual, inv_cov),
        transpose_residual
    )
    return dist_square
