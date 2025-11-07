"""Compute GLEU score for two sequences.

>>> from commoneval import gleu
>>> hyp1 = ['It', 'is', 'a', 'guide', 'to', 'action', 'which', 'ensures', 'that', 'the', 'military', 'always', 'obeys', 'the', 'commands', 'of', 'the', 'party']
>>> ref1a = ['It', 'is', 'a', 'guide', 'to', 'action', 'that', 'ensures', 'that', 'the', 'military', 'will', 'forever', 'heed', 'Party', 'commands']
>>> ref1b = ['It', 'is', 'the', 'guiding', 'principle', 'which', 'guarantees', 'the', 'military', 'forces', 'always', 'being', 'under', 'the', 'command', 'of', 'the', 'Party']
>>> gleu(hyp1, ref1a)
{'true_positive': 8, 'false_positive': 7, 'false_negative': 9}
>>> gleu(hyp1, ref1b)
{'true_positive': 3, 'false_positive': 14, 'false_negative': 14}



"""

from collections import Counter


def gleu(seq1: tuple[str], seq2: tuple[str], n: int = 2) -> dict[str, int]:
    def ngrams(seq, n):
        return [tuple(seq[i : i + n]) for i in range(len(seq) - n + 1)]

    ngrams1 = Counter(ngrams(seq1, n))
    ngrams2 = Counter(ngrams(seq2, n))

    true_positive = 0
    false_positive = 0
    false_negative = 0

    for ng in ngrams1:
        if ng in ngrams2:
            true_positive += min(ngrams1[ng], ngrams2[ng])
            if ngrams1[ng] > ngrams2[ng]:
                false_negative += ngrams1[ng] - ngrams2[ng]
            elif ngrams2[ng] > ngrams1[ng]:
                false_positive += ngrams2[ng] - ngrams1[ng]
        else:
            false_negative += ngrams1[ng]

    for ng in ngrams2:
        if ng not in ngrams1:
            false_positive += ngrams2[ng]

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }
