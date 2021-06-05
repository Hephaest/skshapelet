from sklearn.ensemble import RandomForestClassifier
from xgboost.sklearn import XGBClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

def random_forest_classifier():
    """A static method to return the random forest classifier with default settings.

    Returns:
        output: string, RandomForestClassifier
            A tuple combined with classifier id and instance of RandomForestClassifier.
    """
    return "rf", RandomForestClassifier(n_estimators=100)


def xgb_classifier():
    """A static method to return the eXtreme Gradient Boosting classifier with default settings.
    If you want to GPU, please set tree_method as gpu_hist and gpu_id as 0.

    Returns:
        output: string, XGBClassifier
            A tuple combined with classifier id and instance of XGBClassifier.
    """
    return "xgb", XGBClassifier(use_label_encoder=False, tree_method="hist", gpu_id=-1)


def decision_tree_classifier():
    """A static method to return the decision tree classifier with default settings.

    Returns:
        output: string, DecisionTreeClassifier
            A tuple combined with classifier id and instance of DecisionTreeClassifier.
    """
    return "dt", DecisionTreeClassifier()


def bayesian_network_classifier():
    """A static method to return the bayesian network classifier with default settings.

    Returns:
        output: string, GaussianNB
            A tuple combined with classifier id and instance of GaussianNB.
    """
    return "bn", GaussianNB()


def knn_classifier():
    """A static method to return the KNN classifier with default settings.

    Returns:
        output: string, KNeighborsClassifier
            A tuple combined with classifier id and instance of KNeighborsClassifier.
    """
    return "knn", KNeighborsClassifier()


def svc_classifier():
    """A static method to return the SVC classifier with default settings.

    Returns:
        output: string, SVC
            A tuple combined with classifier id and instance of SVC.
    """
    return "svc", SVC()


def cid_to_classifier(c_id):
    """A static method to return the tuple combined with classifier id and classifier instance to follow the Pipeline's rule.

    Args:
        Id of the current classifier.

    Returns:
        output: tuple
            A tuple combined with a specific classifier id and instance of the required classifier.
    """
    switcher = {
        "rf" : random_forest_classifier,
        "xgb": xgb_classifier,
        "dt" : decision_tree_classifier,
        "bn" : bayesian_network_classifier,
        "knn": KNeighborsClassifier,
        "svc": svc_classifier,
    }

    classifier = switcher.get(c_id, lambda: "Invalid classifier")
    return classifier()