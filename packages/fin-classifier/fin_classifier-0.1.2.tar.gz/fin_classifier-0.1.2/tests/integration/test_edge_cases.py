"""
Testes de casos extremos e edge cases.
"""

import pytest

from src.fin_classifier import Transaction


@pytest.mark.integration
class TestEdgeCases:
    """Testes de casos extremos"""

    def test_empty_description(self, classifier):
        """Testa transação com descrição vazia"""
        trans = Transaction("", 100.00)
        result = classifier.classify(trans)

        # Deve cair no fallback
        assert result.category == "outros"

    def test_zero_amount(self, classifier):
        """Testa transação com valor zero"""
        trans = Transaction("Ajuste Contábil", 0.00)
        result = classifier.classify(trans)

        # Não deve ser classificado como positivo nem negativo
        assert result.category == "outros"

    def test_very_large_amount(self, classifier):
        """Testa transação com valor muito grande"""
        trans = Transaction("Rendimento CRI Juros", 1_000_000_000.00)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"

    def test_very_small_amount(self, classifier):
        """Testa transação com valor muito pequeno"""
        trans = Transaction("Rendimento CRI Juros", 0.01)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"

    def test_negative_very_large_amount(self, classifier):
        """Testa transação com valor negativo muito grande"""
        trans = Transaction("Custo Operacional", -1_000_000_000.00)
        result = classifier.classify(trans)

        assert result.category == "despesas"

    def test_special_characters(self, classifier):
        """Testa descrições com caracteres especiais"""
        transactions = [
            Transaction("Rendimento CRI @#$% Juros", 100.00),
            Transaction("DEB (Extraordinária) Juros", 100.00),
            Transaction("Custo & Despesas", -100.00),
        ]

        results = [classifier.classify(t) for t in transactions]

        assert results[0].category == "ativo_juros"
        assert results[1].category == "ativo_juros"
        assert results[2].category == "despesas"

    def test_unicode_characters(self, classifier):
        """Testa descrições com caracteres unicode"""
        transactions = [
            Transaction("Rendimento CRI José João Juros", 100.00),
            Transaction("Amortização DEB São Paulo", 1000.00),
            Transaction("Custo Operação €", -50.00),
        ]

        results = [classifier.classify(t) for t in transactions]

        assert results[0].category == "ativo_juros"
        assert results[1].category == "ativo_amort"
        assert results[2].category == "despesas"

    def test_multiple_spaces(self, classifier):
        """Testa descrições com múltiplos espaços"""
        trans = Transaction("Rendimento    CRI    Juros", 100.00)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"

    def test_tabs_and_newlines(self, classifier):
        """Testa descrições com tabs e newlines"""
        trans = Transaction("Rendimento\tCRI\nJuros", 100.00)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"

    def test_very_long_description(self, classifier):
        """Testa descrição muito longa"""
        long_desc = "Rendimento CRI " + "x" * 10000 + " Juros"
        trans = Transaction(long_desc, 100.00)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"


@pytest.mark.integration
class TestValidation:
    """Testes de validação"""

    def test_invalid_transaction_description(self):
        """Testa transação com descrição inválida"""
        with pytest.raises(TypeError):
            Transaction(123, 100.00)  # type: ignore

    def test_invalid_transaction_amount(self):
        """Testa transação com valor inválido"""
        with pytest.raises(TypeError):
            Transaction("Test", "100")  # type: ignore

    def test_text_condition_empty_terms(self):
        """Testa condição de texto sem termos"""
        from src.fin_classifier import Text

        with pytest.raises(ValueError):
            Text.contains()

    def test_amount_between_invalid_range(self):
        """Testa Amount.between com intervalo inválido"""
        from src.fin_classifier import Amount

        with pytest.raises(ValueError):
            Amount.between(100, 50)  # min > max

    def test_rule_without_condition(self):
        """Testa regra sem condição (deve usar AlwaysTrue)"""
        from src.fin_classifier import Rule

        rule = Rule()
        trans = Transaction("Test", 100)

        assert rule.matches(trans)  # AlwaysTrue sempre retorna True
