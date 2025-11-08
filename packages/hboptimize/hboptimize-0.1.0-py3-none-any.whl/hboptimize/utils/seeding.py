"""Reproducibility utilities for deterministic runs."""
import random
import numpy as np


def seed_all(seed: int) -> None:
    """
    Set seeds for all random number generators.
    
    Args:
        seed: Random seed
    """
    random.seed(seed)
    np.random.seed(seed)
    
    # If torch is available, seed it too
    try:
        import torch  # type: ignore
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            # Make CUDA operations deterministic
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass
