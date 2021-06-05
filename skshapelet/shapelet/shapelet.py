class Shapelet:
    """The class to describe shapelet behaviours.

    Attributes:
        start_pos: int
            The index of the start position.
        length: int
            The length of the shapelet.
        id: int, optional
            The index of the time series dataset.
        info_gain: int, optional
            The information gain of the shapelet.
        data: ndarray, optional
            Mean array or z-score array of the shapelet.
    """
    def __init__(
            self,
            start_pos,
            length,
            id=0,
            info_gain=None,
            data=None,
            label=None,
    ):
        self.start_pos = start_pos
        self.length = length
        self.id = id
        self.end_pos = start_pos + length
        self.info_gain = info_gain
        self.data = data
        self.label= label

    def __str__(self):
        return (
            "Series ID: {0}, start_pos: {1}, length: {2}, label:{3}, info_gain: {4}"
            " ".format(self.id, self.start_pos, self.length, self.label, self.info_gain)
        )

    def set_id(self, id):
        self.id = id

    def set_ig(self, ig):
        self.info_gain = ig

    def set_data(self, data):
        self.data = data

    def set_label(self, label):
        self.label = label

    def is_self(self, other):
        if not isinstance(other, Shapelet):
            raise TypeError("Type should be Shapelet")
        if self.id == other.id:
            return True
        return False

    def is_intersection(self, other):
        """ Find whether these 2 shapelets have overlapped.
        Args:
            other: Shapelet
                Another shapelet.

        Returns:
            output: Bool
                The check result.
        """
        if not isinstance(other, Shapelet):
            raise TypeError("Type should be Shapelet")
        if other.start_pos <= self.start_pos <= other.end_pos or \
                self.start_pos <= other.start_pos <= self.end_pos:
            return True
        return False

    def is_similar(self, other):
        """ Find whether these 2 shapelets are similar.
        Args:
            other: Shapelet
                Another shapelet.

        Returns:
            output: Bool
                The check result.
        """
        if self.is_self(other) and self.is_intersection(other):
            return True
        return False
