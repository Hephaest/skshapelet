import functools as tool
import numpy as np


def entropy(*classes):
    """Calculate the entropy.

    Args:
        classes: list
            The list of the number of different classes.

    Returns:
        output: float
            The entropy.
    """
    total_num = tool.reduce(lambda x, y: x + y, classes)
    result = 0
    for num_class in classes:
        if num_class > 0:
            p_class = num_class / total_num
            result -= p_class * np.log2(p_class)
    return result