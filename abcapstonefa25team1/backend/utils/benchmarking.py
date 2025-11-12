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
    Measures execution time for a single function call.

    Args:
    func (callable): The function to benchmark.
    *args: Positional arguments to pass to the function.
    **kwargs: Keyword arguments to pass to the function.

    Returns:
    float: Elapsed time in seconds, rounded to six decimal places.
    """
    start = time.time()
    func(*args, **kwargs)             # Execute the target function with its arguments
    end = time.time()
    return round(end - start, 6)      # Return duration in seconds


def average_benchmark(stmt, setup, number = 10):
    """
    Benchmark using timeit — runs code multiple times and returns average time.
    
    Args:
    stmt (str): Code to execute
    setup (str): Setup code executed before running the benchmark.
    number(int, optional): Number of times to run. Defaults to 10.

    Returns:
    float: Average execution time per run in seconds, rounded to six decimal places.
    """
    total_time = timeit.timeit(stmt = stmt, setup = setup, number = number)
    avg_time = total_time /number
    return round(avg_time, 6)

