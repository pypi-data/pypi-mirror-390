"""
Testes unitários para condições de valor.
"""

import pytest

from src.fin_classifier import Amount, Transaction


class TestAmountComparison:
    """Testes para operadores de comparação de valor"""

    def test_gt_greater_than(self):
        """Testa maior que"""
        condition = Amount.gt(100)
        assert condition.matches(Transaction("Test", 150))
        assert not condition.matches(Transaction("Test", 100))
        assert not condition.matches(Transaction("Test", 50))

    def test_lt_less_than(self):
        """Testa menor que"""
        condition = Amount.lt(-100)
        assert condition.matches(Transaction("Test", -150))
        assert not condition.matches(Transaction("Test", -100))
        assert not condition.matches(Transaction("Test", -50))

    def test_gte_greater_or_equal(self):
        """Testa maior ou igual"""
        condition = Amount.gte(100)
        assert condition.matches(Transaction("Test", 150))
        assert condition.matches(Transaction("Test", 100))
        assert not condition.matches(Transaction("Test", 50))

    def test_lte_less_or_equal(self):
        """Testa menor ou igual"""
        condition = Amount.lte(100)
        assert condition.matches(Transaction("Test", 50))
        assert condition.matches(Transaction("Test", 100))
        assert not condition.matches(Transaction("Test", 150))

    def test_eq_equals_with_tolerance(self):
        """Testa igualdade com tolerância"""
        condition = Amount.eq(100, tolerance=0.01)
        assert condition.matches(Transaction("Test", 100.00))
        assert condition.matches(Transaction("Test", 100.005))
        assert not condition.matches(Transaction("Test", 100.02))

    def test_eq_default_tolerance(self):
        """Testa igualdade com tolerância padrão"""
        condition = Amount.eq(100)
        assert condition.matches(Transaction("Test", 100.00))
        assert condition.matches(Transaction("Test", 100.005))

    def test_eq_describe(self):
        """Testa o método describe() para igualdade"""
        condition = Amount.eq(100, tolerance=0.01)
        description = condition.describe()
        assert "100" in description
        assert "0.01" in description


class TestAmountBetween:
    """Testes para Amount.between()"""

    def test_between_inclusive_range(self):
        """Testa intervalo inclusivo"""
        condition = Amount.between(100, 1000)
        assert condition.matches(Transaction("Test", 100))
        assert condition.matches(Transaction("Test", 500))
        assert condition.matches(Transaction("Test", 1000))

    def test_between_outside_range(self):
        """Testa valores fora do intervalo"""
        condition = Amount.between(100, 1000)
        assert not condition.matches(Transaction("Test", 50))
        assert not condition.matches(Transaction("Test", 1500))

    def test_between_invalid_range_raises_error(self):
        """Testa que intervalo inválido lança erro"""
        with pytest.raises(ValueError):
            Amount.between(100, 50)  # min > max

    def test_between_describe(self):
        """Testa o método describe()"""
        condition = Amount.between(100, 1000)
        description = condition.describe()
        assert "100" in description
        assert "1000" in description
        assert "between" in description


class TestAmountSpecial:
    """Testes para condições especiais de valor"""

    def test_positive_greater_than_zero(self):
        """Testa valor positivo"""
        condition = Amount.positive()
        assert condition.matches(Transaction("Test", 0.01))
        assert condition.matches(Transaction("Test", 100))
        assert not condition.matches(Transaction("Test", 0))
        assert not condition.matches(Transaction("Test", -100))

    def test_negative_less_than_zero(self):
        """Testa valor negativo"""
        condition = Amount.negative()
        assert condition.matches(Transaction("Test", -0.01))
        assert condition.matches(Transaction("Test", -100))
        assert not condition.matches(Transaction("Test", 0))
        assert not condition.matches(Transaction("Test", 100))

    def test_positive_describe(self):
        """Testa o método describe() para positivo"""
        condition = Amount.positive()
        assert "positive" in condition.describe().lower()

    def test_negative_describe(self):
        """Testa o método describe() para negativo"""
        condition = Amount.negative()
        assert "negative" in condition.describe().lower()
