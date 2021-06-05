from skshapelet.statistics.entropy import entropy
from skshapelet.statistics import distance
from skshapelet.utils.category import Category

THIS = Category.THIS
OTHER = Category.OTHER


def binary_information_gain(
        orderline,
        num_this_class,
        num_other_class,
        total_num_this_class,
        total_num_other_class,
        ig_threshold
):
    """Calculate the information gain.
    The idea is that we apply the KNN algorithm. We put the rest of class A to split left and put B to split right, respectively.
    However, we also need to switch again since we don't know where class A belongs.

    Args:
        orderline: list
            The list of distance with each time series.
        num_this_class: int
            The number of this class.
        num_other_class:
            The number of other classes.
        total_num_this_class:
            The total number of this class.
        total_num_other_class:
            The total number of other classes.
        ig_threshold: float
            The baseline of information gain.

    Returns:
        output: bool
            Whether the current candidate should be rejected.
    """
    entropy_before = entropy(total_num_this_class, total_num_other_class)

    left_num_this_class = 0
    left_num_other_class = 0

    total_num = total_num_this_class + total_num_other_class

    for num_left in range(0, len(orderline) - 1):
        ts_object = orderline[num_left]

        if ts_object.category is THIS:
            left_num_this_class += 1
        else:
            left_num_other_class += 1

        num_rest_this_class = total_num_this_class - num_this_class

        p_left = (num_left + 1 + num_rest_this_class) / total_num
        p_right = 1 - p_left

        e_left = entropy(
            left_num_this_class + num_rest_this_class,
            left_num_other_class
        )
        e_right = entropy(
            num_this_class - left_num_this_class,
            total_num_other_class - left_num_other_class,
        )

        entropy_after = p_left * e_left + p_right * e_right
        ig_left_this_class = entropy_before - entropy_after

        if ig_left_this_class > ig_threshold:
            return False

        num_rest_other_class = total_num_other_class - num_other_class

        p_left = (num_left + 1 + num_rest_other_class) / total_num
        p_right = 1 - p_left

        e_left = entropy(
            left_num_this_class,
            left_num_other_class + num_rest_other_class
        )
        e_right = entropy(
            total_num_this_class - left_num_this_class,
            num_other_class - left_num_other_class,
        )

        entropy_after = p_left * e_left + p_right * e_right
        ig_right_this_class = entropy_before - entropy_after

        if ig_right_this_class > ig_threshold:
            return False

    return True


def euclidean_distance(this_set, other_set, bsf_dist):
    """Calculate the Euclidean distance between 2 1-D arrays.
    If the distance is larger than bsf_dist, then we end the calculation and return the bsf_dist.

    Args:
        this_set: ndarray
            The array
        other_set: ndarray
            The comparative array.
        bsf_dist:
            The best so far distance.

    Returns:
        output: float
            The accumulation of Euclidean distance.
    """
    sum_dist = 0
    for index in range(0, len(this_set)):
        sum_dist += (this_set[index] - other_set[index]) ** 2
        if sum_dist > bsf_dist:
            return bsf_dist
    return sum_dist


def mahalanobis_distance(X, mean, inv_cov, bsf_dist):
    """Calculate the Mahalanobis distance between 2 1-D arrays.
    If the distance is larger than bsf_dist, then we end the calculation and return the bsf_dist.

    Args:
        X: ndarray
            The comparative array.
        mean: ndarray
            The mean array of the array.
        inv_cov:
            Inverse covariance matrix related to the array.
        bsf_dist:
            The best so far distance.

    Returns:
        output: float
            The accumulation of Mahalanobis distance.
    """
    sum_dist = 0
    for idx in range(0, len(X)):
        sum_dist += distance.mahalanobis_distance(X[idx], mean, inv_cov)
        if sum_dist >= bsf_dist:
            return bsf_dist
    return sum_dist
