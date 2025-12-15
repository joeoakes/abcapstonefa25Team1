import time
import random
import pytest

from abcapstonefa25team1.backend.quantum.classical_shors import Classical_Shors


def is_valid_factor(N, result):
    """Check that (p, q) is a valid non-trivial factorization of N."""
    if not result or not isinstance(result, tuple):
        return False
    p, q = result
    return (p * q == N) and (1 < p < N) and (1 < q < N)


TEST_NUMBERS = [15, 35, 49, 55, 65, 91, 121, 133, 187, 209, 221, 247, 299]


@pytest.mark.load
def test_classical_load_with_summary():
    """
    Repeatedly factor many N values to simulate expected or slightly increased
    workload, while collecting performance metrics for reporting.
    """
    cs = Classical_Shors()

    repeats = 100
    warmup = 5

    print("\n CLASSICAL SHOR LOAD TEST ")

    # Global stats
    total_requests = 0
    total_successes = 0
    total_failures = 0
    all_times = []
    error_types = {"invalid_factor": 0}

    global_start = time.perf_counter()

    for N in TEST_NUMBERS:

        # Warm-up
        for _ in range(warmup):
            cs.shors_classical(N, tries=20)

        for i in range(repeats):
            total_requests += 1
            random.seed(i)

            t0 = time.perf_counter()
            result = cs.shors_classical(N, tries=20)
            t1 = time.perf_counter()

            runtime = t1 - t0
            all_times.append(runtime)

            if is_valid_factor(N, result):
                total_successes += 1
            else:
                total_failures += 1
                error_types["invalid_factor"] += 1

    # Final summary
    global_elapsed = time.perf_counter() - global_start
    avg_response_ms = (sum(all_times) / len(all_times)) * 1000
    min_response_ms = min(all_times) * 1000
    max_response_ms = max(all_times) * 1000
    requests_per_sec = total_requests / global_elapsed

    print("---------------------------")
    print(f"Total Runs:           {total_requests}")
    print(f"Successful:           {total_successes}")
    print(f"Failed:               {total_failures}")
    print(f"Total Time:           {global_elapsed:.4f} seconds")
    print(f"Avg Response Time:    {avg_response_ms:.2f} ms")
    print(f"Fastest Response:     {min_response_ms:.2f} ms")
    print(f"Slowest Response:     {max_response_ms:.2f} ms")
    print(f"Requests/sec:         {requests_per_sec:.2f} rps")
    print("Errors:")
    for err, count in error_types.items():
        print(f" - {err}: {count}")
