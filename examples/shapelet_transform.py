"""
Example mainly mirrors from sktime with a few changes.
"""

from skshapelet.shapelet.shapelet_transform import BinaryShapeletTransform
from skshapelet.utils.validation import check_transform_series
from skshapelet.utils.validation import check_transform_X

import time
import sys
from datetime import datetime
from sklearn.pipeline import Pipeline

from skshapelet.datasets import load_dataset
from skshapelet.classifiers import classifier

dataset_name = "Car"

try:
    train_x, train_y, dist = load_dataset(name=dataset_name, split="train", return_X_y=True)
    test_x, test_y, _ = load_dataset(name=dataset_name, split="test", return_X_y=True, dist=dist)

    X_train, y_train = check_transform_series(train_x, train_y)
    X_test = check_transform_X(test_x)

    classifier = classifier.cid_to_classifier("xgb")

    timestamp = datetime.now()
    model_id = timestamp.strftime('%Y%m%d%H%M%S')

    pipeline = Pipeline(
        [
            (
                "st",
                BinaryShapeletTransform(
                    dataset_name,
                    model_id,
                    time_transform_in_mins=10,
                    num_candidates_to_sample_per_case=10,
                    random_seed=101
                ),
            ),
            classifier,
        ]
    )

    start = time.time()
    pipeline.fit(X_train, y_train)
    end_build = time.time()
    preds = pipeline.predict(X_test)
    end_test = time.time()

    print("Results:")
    print("Correct:")
    correct = sum(preds == test_y)
    print("\t" + str(correct) + "/" + str(len(test_y)))
    print("\t" + str(correct / len(test_y)))
    print("\nTiming:")
    print("\tTo build:   " + str(end_build - start) + " secs")
    print("\tTo predict: " + str(end_test - end_build) + " secs")

except:
    print("Unexpected error:", str(sys.exc_info()[1]).capitalize())