from skshapelet.statistics.entropy import entropy

from skshapelet.utils.category import Category

THIS = Category.THIS
OTHER = Category.OTHER


def binary_information_gain(
        orderline,
        total_num_this_class,
        total_num_other_class
):
    """Calculate the information gain.

    Args:
        orderline: list
            The list of distance with each time series.
        total_num_this_class:
            The total number of this class.
        total_num_other_class:
            The total number of other classes.

    Returns:
        bsf_ig: float
            The best so far information gain.
    """
    entropy_before = entropy(total_num_this_class, total_num_other_class)

    bsf_ig = 0

    left_num_this_class = 0
    left_num_other_class = 0

    total_num = total_num_this_class + total_num_other_class

    for num_left in range(0, len(orderline) - 1):
        ts_object = orderline[num_left]

        if ts_object.category is THIS:
            left_num_this_class += 1
        else:
            left_num_other_class += 1

        p_left = (num_left + 1) / total_num
        p_right = 1 - p_left

        e_left = entropy(
            left_num_this_class,
            left_num_other_class
        )
        e_right = entropy(
            total_num_this_class - left_num_this_class,
            total_num_other_class - left_num_other_class,
        )

        entropy_after = p_left * e_left + p_right * e_right
        current_ig = entropy_before - entropy_after
        bsf_ig = max(current_ig, bsf_ig)

    return bsf_ig
