import numpy as np
from typing import Dict


def histogram(a: np.ndarray) -> Dict[int, int]:
    unique, counts = np.unique(a, return_counts=True)
    return dict(zip(unique, counts))
