# -----------------------------------------------------------
# Project:
# Purpose Details: Provides utility functions for benchmarking
#                  execution time of fucntions in the project.
# Course: CMPSC 488
# Author: Kamila Anarkulova
# Date Developed: October 28, 2025
# Last Date Changed: October 28, 2025
# Revision: 1.0 - Initial version, created benchmarking functions
# -----------------------------------------------------------


import time
import timeit

def benchmark_function(func, *args, **kwargs):
    """
    Measures execution time for a dingle function call.
    Returns elapsed time in seconds.
    """
    start = time.time()
    func(*args, **kwargs)             # Execute the target function with its arguments
    end = time.time()
    return round(end - start, 6)      # Return duration in seconds


def average_benchmark(stmt, setup, number = 10):
    """
    Benchmark using timeit — runs code multiple times and returns average time.
    """
    total_time = timeit.timeit(stmt = stmt, setup = setup, number = number)
    avg_time = total_time /number
    return round(avg_time, 6)
