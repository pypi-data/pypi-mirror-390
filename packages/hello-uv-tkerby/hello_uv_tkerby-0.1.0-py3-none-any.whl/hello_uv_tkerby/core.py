import numpy as np


def add_one(x):
    return x + 1


def calculate_mean(numbers):
    """Calculate the mean of a list of numbers using numpy.
    
    Args:
        numbers: A list or array of numbers
        
    Returns:
        The mean as a float
    """
    return np.mean(numbers)
