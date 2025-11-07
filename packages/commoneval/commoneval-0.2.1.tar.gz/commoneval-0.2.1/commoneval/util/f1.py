"""Infrastructure for scoring recall, precision, and F1 score."""


def precision(true_positives: int, false_positives: int) -> float:
    denom = true_positives + false_positives
    return true_positives / denom if denom else 0.0


def recall(true_positives: int, false_negatives: int) -> float:
    denom = true_positives + false_negatives
    return true_positives / denom if denom else 0.0


def f1(recall: float, precision: float) -> float:
    denom = precision + recall
    return ((2 * precision * recall) / denom) if denom else 0.0
