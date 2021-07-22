__author__ = ["Miao Cai"]
__all__ = [
    "BinaryShapeletTransform",
]

import warnings
import numpy as np
import pandas as pd

from sklearn.utils import check_random_state
from sklearn.utils.multiclass import class_distribution

from sktime.transformations.base import _PanelToTabularTransformer

from skshapelet.utils.validation import check_min_length
from skshapelet.utils.scheduler import round_robin
from skshapelet.utils.timer import Timer
from skshapelet.utils.TimeSeries import TimeSeries
from skshapelet.utils.category import Category

from skshapelet.shapelet.shapelet_set import ShapeletSet
from skshapelet.shapelet.shapelet import Shapelet

from skshapelet.statistics import information_gain
from skshapelet.statistics import early_abandon
from skshapelet.statistics import distance

from skshapelet.shapelet.filehelper import write_shapelets_to_csv

import mass_ts as mts

candidate_set = {}
THIS = Category.THIS
OTHER = Category.OTHER


class TSObject():
    """The class to describe TSObject behaviours.

    Attributes:
        bsf_dist: int
            The best so far distance.
        category: Category
            The category of this time series.
    """
    def __init__(self, bsf_dist, category):
        self.bsf_dist = bsf_dist
        self.category = category


class BinaryShapeletTransform(_PanelToTabularTransformer):
    """BinaryShapeletTransform.
    This implementation is based on sktime.

    Attributes:
        min_shapelet_length: int, optional
            The best so far distance.
        max_shapelet_length: int, optional
            The maximum length of the shapelet.
        max_shapelets_to_store_per_class: int, optional
            The maximum shapelet size for each class.
        time_transform_in_mins: int, optional
            The maximum transformation time.
        num_candidates_to_sample_per_case: int, optional
            The maximum candidates for each time series.
        random_seed: int, optional
            The random seed.
    """
    def __init__(
            self,
            dataset_name,
            model_id,
            min_shapelet_length=3,
            max_shapelet_length=np.inf,
            max_shapelets_to_store_per_class=200,
            time_transform_in_mins=None,
            num_candidates_to_sample_per_case=None,
            random_seed=None,
    ):
        self.dataset_name = dataset_name
        self.model_id = model_id
        self.min_shapelet_length = min_shapelet_length
        self.max_shapelet_length = max_shapelet_length
        self.max_shapelets_to_store_per_class = max_shapelets_to_store_per_class
        self.num_candidates_to_sample_per_case = num_candidates_to_sample_per_case
        self.time_transform_in_mins = time_transform_in_mins
        self.random_state = check_random_state(random_seed)
        self.predefined_ig_rejection_level = 0.05
        self.shapelets = []
        self.is_fitted_ = False
        super(BinaryShapeletTransform, self).__init__()

    def fit(self, X, y=None):

        is_univariate = X.shape[1] == 1

        total_num_ins = len(y)

        distinct_class = class_distribution(np.asarray(y).reshape(-1, 1))[0][0]

        stack_by_class = {i: ShapeletSet() for i in distinct_class}

        num_ins_per_class, ts_order = BinaryShapeletTransform.random_shuffle_class_case_policy(
            y,
            self.random_state,
            distinct_class
        )

        if self.time_transform_in_mins is not None:
            timer = Timer(self.time_transform_in_mins * 60)
        else:
            timer= Timer()

        timer.start()
        time_finished = False

        for ts in ts_order:
            this = ts
            this.len = len(X[this.id][0])
            print("id: ", this.id)

            if not is_univariate:
                cov = np.cov(X[this.id], bias=False)
                this.inv_cov = np.linalg.inv(cov)

            num_this_class = num_ins_per_class[this.label] - 1
            num_other_class = total_num_ins - num_ins_per_class[this.label]

            this_max_len = check_min_length(self.max_shapelet_length, this.len)

            candidates = BinaryShapeletTransform.generate_candidates_by_cache(
                this.len,
                self.min_shapelet_length,
                this_max_len
            )

            random_candidates = BinaryShapeletTransform.random_shapelet_selection(
                candidates,
                self.num_candidates_to_sample_per_case,
                self.random_state
            )

            for candidate in random_candidates:

                ig_threshold = BinaryShapeletTransform.update_ig_threshold(
                    self.predefined_ig_rejection_level,
                    stack_by_class,
                    this.label
                )

                orderline = []

                num_visited_this_class = 0
                num_visited_other_class = 0

                candidate_rejected = False

                candidate.set_id(this.id)
                candidate.set_label(this.label)

                X_subseries = X[this.id][:, candidate.start_pos: candidate.start_pos + candidate.length]

                if is_univariate:
                    candidate.set_data(X_subseries.flatten())
                else:
                    mean = np.mean(X_subseries.T, axis=0)
                    candidate.set_data((mean, this.inv_cov))

                for other in ts_order:
                    if other.id == this.id:
                        # Skip self
                        continue

                    if y[other.id] == this.label:
                        num_visited_this_class += 1
                        class_label = Category.THIS
                    else:
                        num_visited_other_class += 1
                        class_label = Category.OTHER

                    if is_univariate:
                        dists = mts.mass2(X[other.id].flatten(), candidate.data)
                        bsf_dist = np.amin(dists).astype(np.float32)
                    else:
                        bsf_dist = BinaryShapeletTransform.find_distance(
                            candidate,
                            X[other.id],
                            is_univariate,
                            candidate.data
                        )

                    orderline.append(TSObject(bsf_dist, class_label))
                    orderline.sort(key=lambda obj: obj.bsf_dist)

                    if len(orderline) > 2:
                        candidate_rejected = early_abandon.binary_information_gain(
                            orderline,
                            num_visited_this_class,
                            num_visited_other_class,
                            num_this_class,
                            num_other_class,
                            ig_threshold
                        )

                        if candidate_rejected:
                            break

                if candidate_rejected is False:
                    ig = information_gain.binary_information_gain(
                        orderline,
                        num_this_class,
                        num_other_class,
                    )

                    candidate.set_ig(ig)
                    stack_by_class[this.label].accept(candidate)

                    if stack_by_class[this.label].get_size() > \
                            self.max_shapelets_to_store_per_class * 3:
                        stack_by_class[this.label].discard()

                if timer.is_end():
                    time_finished = True
                    timer.stop()
                    break

            if time_finished:
                break

        for label in distinct_class:
            shapelets = BinaryShapeletTransform.remove_self_similar_shapelets(
                stack_by_class[label].get_shapelets()
            )
            BinaryShapeletTransform.reduce_if_needed(
                shapelets,
                self.max_shapelets_to_store_per_class
            )

            self.shapelets.extend(shapelets)

        self.shapelets.sort(key=lambda x: x.info_gain, reverse=True)
        self.is_fitted_ = True

        if len(self.shapelets) == 0:
            warnings.warn(
                "No valid shapelets were extracted from this dataset and "
                "calling the transform method "
                "will raise an Exception. Please re-fit the transform with "
                "other data and/or "
                "parameter options."
            )

        print("Fit time: ", timer.till_now())

        self._is_fitted = True

        # Save shapelets
        write_shapelets_to_csv(
            self.dataset_name,
            self.model_id,
            distinct_class,
            self.shapelets
        )

        return self

    @staticmethod
    def random_shuffle_class_case_policy(y, random_state, distinct_class):
        """Suffle the class case by random state.

        Attributes:
            y: ndarray
                The numpy array.
            random_state: RandomState
                The instance of RandomState.
            distinct_class: list
                A list contains all distinct class labels.

        Returns:
            num_ins_per_class: int
                The number of instance in each class.
            ts_order: list
                The order of the time series.
        """
        ins_ids_by_class = {i: np.where(y == i)[0] for i in distinct_class}

        for i in range(len(distinct_class)):
            random_state.shuffle(ins_ids_by_class[distinct_class[i]])

        num_ins_per_class = {i: len(ins_ids_by_class[i]) for i in ins_ids_by_class}
        id_order = round_robin(
            *[list(v) for k, v in ins_ids_by_class.items()]
        )
        ts_order = [TimeSeries(i, y[i]) for i in id_order]
        return num_ins_per_class, ts_order

    @staticmethod
    def generate_candidates_by_cache(X_len, min_len, max_len):
        """Generate candidates one time, use it forever:)

        Attributes:
            X_len: int
                The length of current time series.
            min_len: int
                The minimum length.
            max_len: int
                The maximum length.

        Returns:
            output: list
                Contain all possible candidates with a specific length range.
        """
        candidates = candidate_set.get(X_len)

        if candidates is None:
            candidate_set[X_len] = [
                Shapelet(
                    start_pos,
                    length
                )
                for start_pos in range(
                    0, X_len - min_len + 1
                )
                for length in range(
                    min_len, max_len + 1
                )
                if start_pos + length <= X_len
            ]

        return candidate_set[X_len]

    @staticmethod
    def random_shapelet_selection(candidates, num_require_per_case, random_state):
        """Select shapelet by random state.

        Attributes:
            candidates: list
                The list of all possible candidates.
            num_require_per_case: int
                The required number of each time series.
            random_state: RandomState
                The instance of RandomState.

        Returns:
            output: list
                Return a list of selected candidates.
        """
        if num_require_per_case is None:
            return candidates

        candidate_len = min(
            num_require_per_case,
            len(candidates)
        )

        ids = list(
            random_state.choice(
                list(range(0, len(candidates))),
                candidate_len,
                replace=False,
            )
        )
        return [candidates[id] for id in ids]

    @staticmethod
    def update_ig_threshold(threshold, stack, label):
        """Update the information gain threshold if needed.

        Attributes:
            threshold: float
                The baseline of the information gain.
            stack: list
                The list stores shapelets.
            label: int
                The label of the current class.

        Returns:
            threshold: float
                Return new information gain threshold.
        """
        if stack[label].get_size() >= threshold:
            worst_shapelet = stack[label].last_shapelet()
            return max(
                worst_shapelet.info_gain,
                threshold
            )
        return threshold

    @staticmethod
    def find_distance(
            shapelet,
            other_ts,
            is_univariate,
            shapelet_data
    ):
        """Find the shortest distance.
        The origin point is where the shapelet exactly is. We will scan left first and then scan right.

        Attributes:
            shapelet: Shapelet
                The current candidate.
            other_ts: ndarray
                The another time series.
            is_univariate: bool
                The property of this dataset.
            shapelet_data: ndarray
                The information that shapelet carries.

        Returns:
            output: float
                Return the shortest distance.
        """
        shapelet_len = shapelet.length
        other_ts_len = len(other_ts[0])

        left_end = shapelet.start_pos
        right_start = shapelet.start_pos
        right_end = other_ts_len - shapelet_len + 1

        left_bsf_dist = BinaryShapeletTransform.distance_scan(
            0,
            left_end,
            other_ts,
            shapelet_len,
            shapelet_data,
            is_univariate
        )

        right_bsf_dist = BinaryShapeletTransform.distance_scan(
            right_start,
            right_end,
            other_ts,
            shapelet_len,
            shapelet_data,
            is_univariate
        )

        return min(left_bsf_dist, right_bsf_dist)

    @staticmethod
    def distance_scan(
            start,
            end,
            other_ts,
            shapelet_len,
            shapelet_data,
            is_univariate
    ):
        """Scan distance between 2 time series.

        Attributes:
            start: Shapelet
                Start position.
            end: ndarray
                End position.
            other_ts: ndarray
                The another time series.
            shapelet_len: int
                The length of the shapelet
            shapelet_data: ndarray
                The information that shapelet carries with.
            is_univariate: bool
                The property of this dataset.

        Returns:
            bsf_dist: float
                Return the shortest distance.
        """
        bsf_dist = np.inf
        for pos in range(start, end):
            if is_univariate:
                other_ts_data = distance.zscore(
                    other_ts[:, pos: pos + shapelet_len].flatten()
                )
                dist = distance.euclidean_distance(
                    shapelet_data,
                    other_ts_data
                )
            else:
                (mean, inv_cov) = shapelet_data
                dist = early_abandon.mahalanobis_distance(
                    other_ts[:, pos: pos + shapelet_len].T,
                    mean,
                    inv_cov,
                    bsf_dist
                )
            bsf_dist = min(dist, bsf_dist)
        return bsf_dist

    @staticmethod
    def discard_if_needed(stack, num_max_size):
        if stack.get_size() > num_max_size:
            stack.discard()

    @staticmethod
    def reduce_if_needed(shapelets, num_max_size):
        if len(shapelets) > num_max_size:
            del shapelets[num_max_size:]

    @staticmethod
    def remove_self_similar_shapelets(shapelets):
        """Remove self similar shapelets.

        Attributes:
            shapelets: list
                The list of Shapelet instances.

        Returns:
            distinct_shapelets: list
                Return a list that contains distinct Shapelet instances.
        """
        distinct_shapelets = []

        check_point = 0
        for candidate in shapelets:
            can_add = True
            for pre_point in range(0, check_point):
                shapelet = shapelets[pre_point]
                if candidate.is_similar(shapelet):
                    can_add = False
                    break

            if can_add:
                distinct_shapelets.append(candidate)
            check_point += 1

        return distinct_shapelets

    def transform(self, X, y=None):
        """Transform a set of data into distances to each extracted shapelet.
        Test dataset should be transformed as a distance matrix.
        This mirrors the sktime implementation.

        Args:
            x: pandas DataFrame
                The input dataframe to transform
            y: pandas DataFrame or None, optional
                The test class label array.

        Returns:
            output: pandas DataFrame
                The transformed dataframe in tabular format.
        """
        self.check_is_fitted()

        is_univariate = X.shape[1] == 1

        if len(self.shapelets) == 0:
            raise RuntimeError(
                "No shapelets were extracted in fit that exceeded the "
                "minimum information gain threshold. Please retry with other "
                "data and/or parameter settings."
            )

        for s in self.shapelets:
            print(s.__str__())

        output = np.zeros(
            [len(X), len(self.shapelets)],
            dtype=np.float32,
        )

        for i in range(0, len(X)):
            this_series = X[i]

            for s in range(0, len(self.shapelets)):
                min_dist = np.inf
                this_shapelet_length = self.shapelets[s].length

                if is_univariate:
                    dists = mts.mass2(this_series.flatten(), self.shapelets[s].data)
                    min_dist = np.amin(dists).astype(np.float32)
                else:
                    for start_pos in range(
                            0, len(this_series[0]) - this_shapelet_length + 1
                    ):
                        (mean, inv_cov) = self.shapelets[s].data
                        dist = early_abandon.mahalanobis_distance(
                            this_series[:, start_pos: start_pos + this_shapelet_length].T,
                            mean,
                            inv_cov,
                            min_dist
                        )
                        min_dist = min(min_dist, dist)

                output[i][s] = min_dist

        return pd.DataFrame(output)

    def get_shapelets(self):
        return self.shapelets