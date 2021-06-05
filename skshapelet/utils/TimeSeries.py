class TimeSeries:
    """The class to describe time series behaviours.

    Attributes:
        id: int
            The index of the time series dataset.
        label: int
            The label of the time series.
        len: int, optional
            The length of the time series.
        inv_cov: ndarray, optional
            Inverse covariance matrix related to the time series.
    """
    def __init__(self, id, label, len=0, inv_cov=None):
        self.id = id
        self.label = label
        self.len = len
        self.inv_cov = inv_cov