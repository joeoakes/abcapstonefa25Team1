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
    """Basic correctness smoke test for small N."""
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
    """Load-style test across multiple N values with result table output."""
    
    q = Quantum_Shors()
    test_numbers = [15, 21]
    repeats = 3

    print("\n--- QUANTUM SHOR LOAD TEST ---")

    for N in test_numbers:
        successes = 0
        start = time.perf_counter()

        for i in range(repeats):
            result = q.run_shors_algorithm(N, max_attempts=5)
            if is_valid_factor(N, result):
                successes += 1

        elapsed = time.perf_counter() - start
        rate = repeats / max(elapsed, 1e-9)

        # Table-like output (aligned columns)
        print(
            f"N={N:<4} | successes={successes:>2}/{repeats} "
            f"| time={elapsed:.3f}s | rate={rate:.2f} runs/s"
        )

        assert successes >= 1, f"Quantum Shor had zero successes for N={N}"
