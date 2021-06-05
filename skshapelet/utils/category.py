from enum import Enum


class Category(Enum):
    """The category for KNN type classification.

    Attributes:
        THIS: int
            This aims to refer to the current class.
        OTHER: int
            This aims to refer to other classes.
    """
    THIS = 1
    OTHER = 0