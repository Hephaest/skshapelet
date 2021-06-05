from skshapelet.shapelet.shapelet import Shapelet


class ShapeletSet:
    """The class to describe ShapeletSet behaviours.
    To save time, we sort the list each time we insert a shapelet.

    Attributes:
        shapelets: list
            A list to store the acceptable shapelet.
    """
    def __init__(self):
        self.shapelets = []

    def accept(self, shapelet):
        if not isinstance(shapelet, Shapelet):
            raise TypeError("Only accept shapelets instance!")

        self.shapelets.append(shapelet)
        self.shapelets.sort(key = lambda s: s.info_gain, reverse=True)

    def discard(self):
        if self.shapelets.__len__() == 0:
            raise IndexError("The shapelets shapelets is empty!")

        self.shapelets = self.shapelets[:-1]
        return self.shapelets

    def last_shapelet(self):
        if self.shapelets.__len__() == 0:
            raise IndexError("The shapelets shapelets is empty!")

        return self.shapelets[-1]

    def get_size(self):
        return self.shapelets.__len__()

    def get_shapelets(self):
        return self.shapelets