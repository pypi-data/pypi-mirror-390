"""
Testes unitários para operadores lógicos de condições.
"""

import pytest

from src.fin_classifier import Amount, Text, Transaction


class TestAndOperator:
    """Testes para operador & (AND)"""

    def test_and_both_conditions_true(self):
        """Testa quando ambas as condições são verdadeiras"""
        condition = Text.contains("banco") & Amount.positive()
        assert condition.matches(Transaction("Banco do Brasil", 100))

    def test_and_first_condition_false(self):
        """Testa quando primeira condição é falsa"""
        condition = Text.contains("banco") & Amount.positive()
        assert not condition.matches(Transaction("Supermercado", 100))

    def test_and_second_condition_false(self):
        """Testa quando segunda condição é falsa"""
        condition = Text.contains("banco") & Amount.positive()
        assert not condition.matches(Transaction("Banco do Brasil", -100))

    def test_and_both_conditions_false(self):
        """Testa quando ambas as condições são falsas"""
        condition = Text.contains("banco") & Amount.positive()
        assert not condition.matches(Transaction("Supermercado", -100))

    def test_and_multiple_conditions(self):
        """Testa AND com múltiplas condições encadeadas"""
        condition = Text.contains("banco") & Amount.positive() & Amount.gt(50)
        assert condition.matches(Transaction("Banco do Brasil", 100))
        assert not condition.matches(Transaction("Banco do Brasil", 30))


class TestOrOperator:
    """Testes para operador | (OR)"""

    def test_or_first_condition_true(self):
        """Testa quando primeira condição é verdadeira"""
        condition = Text.contains("banco") | Text.contains("caixa")
        assert condition.matches(Transaction("Banco do Brasil", 100))

    def test_or_second_condition_true(self):
        """Testa quando segunda condição é verdadeira"""
        condition = Text.contains("banco") | Text.contains("caixa")
        assert condition.matches(Transaction("Caixa Econômica", 100))

    def test_or_both_conditions_true(self):
        """Testa quando ambas as condições são verdadeiras"""
        condition = Text.contains("banco") | Text.contains("caixa")
        assert condition.matches(Transaction("Banco Caixa", 100))

    def test_or_no_condition_true(self):
        """Testa quando nenhuma condição é verdadeira"""
        condition = Text.contains("banco") | Text.contains("caixa")
        assert not condition.matches(Transaction("Supermercado", 100))

    def test_or_multiple_conditions(self):
        """Testa OR com múltiplas condições encadeadas"""
        condition = Text.contains("banco") | Text.contains("caixa") | Text.contains("itau")
        assert condition.matches(Transaction("Banco", 100))
        assert condition.matches(Transaction("Caixa", 100))
        assert condition.matches(Transaction("Itau", 100))
        assert not condition.matches(Transaction("Bradesco", 100))


class TestNotOperator:
    """Testes para operador ~ (NOT)"""

    def test_not_condition_true(self):
        """Testa inversão de condição verdadeira"""
        condition = ~Text.contains("custodia")
        assert condition.matches(Transaction("Taxa Bolsa", -10))

    def test_not_condition_false(self):
        """Testa inversão de condição falsa"""
        condition = ~Text.contains("custodia")
        assert not condition.matches(Transaction("Taxa Custodia", -10))

    def test_not_double_negation(self):
        """Testa dupla negação"""
        condition = ~~Text.contains("banco")
        # Double negation should be equivalent to original
        assert condition.matches(Transaction("Banco", 100))
        assert not condition.matches(Transaction("Supermercado", 100))


class TestComplexComposition:
    """Testes para composição complexa de operadores"""

    def test_complex_composition_1(self):
        """Testa (A | B) & C"""
        condition = (Text.contains("a") | Text.contains("b")) & Amount.positive()
        assert condition.matches(Transaction("a", 100))
        assert condition.matches(Transaction("b", 100))
        assert not condition.matches(Transaction("a", -100))
        assert not condition.matches(Transaction("c", 100))

    def test_complex_composition_2(self):
        """Testa A | (B & C)"""
        condition = Text.contains("a") | (Text.contains("b") & Amount.positive())
        assert condition.matches(Transaction("a", -100))  # Diferente de composition_1
        assert condition.matches(Transaction("b", 100))
        assert not condition.matches(Transaction("b", -100))
        assert not condition.matches(Transaction("c", 100))

    def test_complex_with_negation(self):
        """Testa composição com negação"""
        condition = Text.any_of("cri", "deb") & Text.contains("juros") & Amount.positive() & ~Text.contains("provisao")
        assert condition.matches(Transaction("Rendimento CRI Juros", 100))
        assert condition.matches(Transaction("DEB Juros Mensais", 100))
        assert not condition.matches(Transaction("CRI Juros Provisao", 100))
        assert not condition.matches(Transaction("CRI Juros", -100))
        assert not condition.matches(Transaction("CRI Amortizacao", 100))

    def test_operator_precedence_matters(self):
        """Testa que precedência de operadores é importante"""
        # (A | B) & C vs A | (B & C) devem produzir resultados diferentes
        cond1 = (Text.contains("a") | Text.contains("b")) & Amount.positive()
        cond2 = Text.contains("a") | (Text.contains("b") & Amount.positive())

        trans_negative_a = Transaction("a", -100)
        assert cond1.matches(trans_negative_a) != cond2.matches(trans_negative_a)

    def test_describe_complex_condition(self):
        """Testa o método describe() para condição complexa"""
        condition = (Text.contains("a") | Text.contains("b")) & Amount.positive()
        description = condition.describe()
        assert "AND" in description
        assert "OR" in description
