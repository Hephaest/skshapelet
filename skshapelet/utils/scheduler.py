from itertools import zip_longest


def round_robin(*iterables):
    """The round robin scheduler.
    This mirrors the sktime implementation.

    Attributes:
        iterables: list
            The index with a dist (each class with its own instance ids)

    Returns:
        output: list
            Return a list of time series index.
    """
    sentinel = object()
    return (
        a
        for x in zip_longest(*iterables, fillvalue=sentinel)
        for a in x
        if a != sentinel
    )
