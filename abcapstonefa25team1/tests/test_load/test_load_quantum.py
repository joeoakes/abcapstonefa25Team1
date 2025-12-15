import pytest
import time
from abcapstonefa25team1.backend.quantum.quantum_shors import Quantum_Shors


def is_valid_factor(N, result):
    """Return True if result is a valid non-trivial factor pair of N."""
    return (
        result
        and isinstance(result, tuple)
        and result[0] * result[1] == N
        and 1 < result[0] < N
        and 1 < result[1] < N
    )


def test_quantum_shors_small_numbers():
    """Basic correctness test for small N."""
    q = Quantum_Shors()
    test_numbers = [15, 21]
    successes = 0

    for N in test_numbers:
        result = q.run_shors_algorithm(N, max_attempts=5)
        if is_valid_factor(N, result):
            successes += 1

    assert successes >= 1, "Quantum Shor failed all small-number tests."


@pytest.mark.slow
def test_quantum_shors_load_multi():
    """
    Stress-test the quantum Shor simulation under expected or slightly
    elevated workload.
    """

    q = Quantum_Shors()

    test_numbers = [15, 33, 39, 55, 91, 121]
    repeats = 30
    warmup = 2

    print("\n QUANTUM SHOR LOAD TEST ")

    # Global metrics
    total_requests = 0
    total_successes = 0
    total_failures = 0
    all_times = []
    error_types = {"invalid_factor": 0}

    global_start = time.perf_counter()

    for N in test_numbers:

        # Warm-up (not timed)
        for _ in range(warmup):
            q.run_shors_algorithm(N, max_attempts=5)

        # Measured runs
        for _ in range(repeats):
            total_requests += 1

            t0 = time.perf_counter()
            result = q.run_shors_algorithm(N, max_attempts=5)
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
    avg_ms = (sum(all_times) / len(all_times)) * 1000
    min_ms = min(all_times) * 1000
    max_ms = max(all_times) * 1000
    rps = total_requests / global_elapsed

    print("---------------------------")
    print(f"Total Runs:           {total_requests}")
    print(f"Successful:           {total_successes}")
    print(f"Failed:               {total_failures}")
    print(f"Total Time:           {global_elapsed:.4f} seconds")
    print(f"Avg Response Time:    {avg_ms:.2f} ms")
    print(f"Fastest Response:     {min_ms:.2f} ms")
    print(f"Slowest Response:     {max_ms:.2f} ms")
    print(f"Requests/sec:         {rps:.2f} rps")
    print("Errors:")
    for err, count in error_types.items():
        print(f" - {err}: {count}")
