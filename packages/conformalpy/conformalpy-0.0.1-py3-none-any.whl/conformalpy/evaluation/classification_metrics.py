import numpy as np

def coverage_score(prediction_sets, true_labels):
    """
    Compute empirical coverage: proportion of prediction sets that contain the true label.
    """
    return np.mean([
        true_labels[i] in prediction_sets[i]
        for i in range(len(true_labels))
    ])


def average_set_size(prediction_sets):
    """
    Compute average size of prediction sets.
    """
    return np.mean([len(s) for s in prediction_sets])


def one_class_correct_score(prediction_sets, true_labels):
    """
    Compute proportion of prediction sets with only the correct class.
    """
    return np.mean([
        len(prediction_sets[i]) == 1 and true_labels[i] in prediction_sets[i]
        for i in range(len(true_labels))
    ])


def one_class_incorrect_score(prediction_sets, true_labels):
    """
    Compute proportion of prediction sets with only one (wrong) class.
    """
    return np.mean([
        len(prediction_sets[i]) == 1 and true_labels[i] not in prediction_sets[i]
        for i in range(len(true_labels))
    ])


def two_class_sets_score(prediction_sets):
    """
    Compute proportion of prediction sets with exactly 2 classes.
    """
    return np.mean([
        len(s) == 2 for s in prediction_sets
    ])


def empty_sets_score(prediction_sets):
    """
    Compute proportion of prediction sets that are empty.
    """
    return np.mean([
        len(s) == 0 for s in prediction_sets
    ])

def conformal_classification_summary(prediction_sets, true_labels):
    """
    Compute all standard conformal classification evaluation metrics.

    Returns
    -------
    dict
        Dictionary with:
            - coverage
            - avg_set_size
            - one_class_correct
            - one_class_incorrect
            - two_class_sets
            - empty_sets
    """
    return {
        'coverage': coverage_score(prediction_sets, true_labels),
        'avg_set_size': average_set_size(prediction_sets),
        'one_class_correct': one_class_correct_score(prediction_sets, true_labels),
        'one_class_incorrect': one_class_incorrect_score(prediction_sets, true_labels),
        'two_class_sets': two_class_sets_score(prediction_sets),
        'empty_sets': empty_sets_score(prediction_sets),
    }
