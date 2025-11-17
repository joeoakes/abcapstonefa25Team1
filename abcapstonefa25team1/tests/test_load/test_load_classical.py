import time
import random
import pytest

#  Import path
from abcapstonefa25team1.backend.quantum.classical_shors import Classical_Shors


def is_valid_factor(N, result):
    """Check that (p, q) is a valid non-trivial factorization of N."""
    if not result or not isinstance(result, tuple):
        return False
    p, q = result
    return (p * q == N) and (1 < p < N) and (1 < q < N)


# A set of test numbers 
TEST_NUMBERS = [15, 21, 33, 35, 39, 49, 55, 65, 77, 91, 121]


@pytest.mark.parametrize("N", TEST_NUMBERS)
def test_classical_correctness(N):
    """Ensure Classical Shor finds valid factors for multiple N values."""
    cs = Classical_Shors()
    result = cs.shors_classical(N, tries=20)
    assert is_valid_factor(N, result), f"Failed to factor N={N}, got: {result}"


def test_classical_load_multiple_values():
    """Load-style test across several N values, showing throughput."""
    cs = Classical_Shors()
    repeats = 25

    print("\n--- CLASSICAL SHOR LOAD TEST ---")
    for N in TEST_NUMBERS:
        successes = 0
        start = time.perf_counter()
        for i in range(repeats):
            random.seed(i)
            result = cs.shors_classical(N, tries=20)
            if is_valid_factor(N, result):
                successes += 1
        elapsed = time.perf_counter() - start
        rate = repeats / max(elapsed, 1e-9)
        print(f"N={N:<4} | successes={successes:>2}/{repeats} | "
              f"time={elapsed:.4f}s | rate={rate:.1f} runs/s")
        assert successes >= 1, f"No successful factorizations for N={N}"
