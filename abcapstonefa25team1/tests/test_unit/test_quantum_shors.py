import pytest
from unittest.mock import MagicMock, patch
from abcapstonefa25team1.backend.quantum.quantum_shors import Quantum_Shors


def test_even_number_shortcut():
    qs = Quantum_Shors()
    assert qs.shors_quantum(20) == (2, 10)


def test_prime_returns_none():
    qs = Quantum_Shors()
    assert qs.shors_quantum(13) is None


def test_perfect_power():
    qs = Quantum_Shors()
    # 27 = 3^3
    assert qs.shors_quantum(27) == (3, 9)


def test_gcd_lucky_factor():
    qs = Quantum_Shors()
    # Force a to share gcd > 1 with N
    with patch("random.randint", return_value=7):
        assert qs.shors_quantum(21) == (7, 3)


def test_enable_gpu():
    qs = Quantum_Shors()
    qs.enable_gpu(True)
    assert qs.use_gpu is True
    qs.enable_gpu(False)
    assert qs.use_gpu is False


@patch(
    "abcapstonefa25team1.backend.quantum.quantum_shors.Quantum_Shors.quantum_period_finding"
)
def test_shors_quantum_period_success(mock_period):
    qs = Quantum_Shors()
    mock_period.return_value = 4  # even → valid

    # Avoid random
    with patch("random.randint", return_value=2):
        result = qs.shors_quantum(15)
        assert result in [(3, 5), (5, 3)]


def test_shors_quantum_period_odd():
    qs = Quantum_Shors()
    with patch.object(qs, "quantum_period_finding", return_value=3):
        with patch("random.randint", return_value=2):
            assert qs.shors_quantum(15) is None


def test_run_shors_algorithm_success():
    qs = Quantum_Shors()
    with patch.object(qs, "shors_quantum", return_value=(3, 5)):
        assert qs.run_shors_algorithm(15) == (3, 5)


def test_run_shors_algorithm_fail():
    qs = Quantum_Shors()
    with patch.object(qs, "shors_quantum", return_value=None):
        assert qs.run_shors_algorithm(21, max_attempts=3) is None
