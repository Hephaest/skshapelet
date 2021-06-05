from enum import Enum
from time import time
import numpy as np


class State(Enum):
    """The status for the timer. This class is inherited from Enum.

    Attributes:
        activate: int
            Let the timer engine start.
        deactivate: int
            The timer shutdown its engine.
    """
    activate = 1
    deactivate = 0


class Timer:
    """The class to describe timer behaviours.

    Attributes:
        state: int
            The status of the timer.
        start_time: int
            When the timer starts to work. The number is presented by second.
        countdown: int, optional
            The minutes for the countdown.
    """
    def __init__(self, countdown=np.inf):
        self.state = State.deactivate
        self.start_time = 0
        self.countdown = countdown

    def start(self):
        self.state = State.activate
        self.start_time = time()

    def stop(self):
        self.state = State.deactivate

    def is_end(self):
        time_taken = time() - self.start_time
        return time_taken - self.countdown > 0

    def till_now(self):
        return time() - self.start_time
