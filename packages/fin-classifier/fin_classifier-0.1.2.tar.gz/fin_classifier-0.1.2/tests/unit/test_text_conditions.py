"""
Testes unitários para condições de texto.
"""

import pytest

from src.fin_classifier import Text, Transaction


class TestTextContains:
    """Testes para Text.contains()"""

    def test_contains_all_terms_present(self):
        """Testa quando todos os termos estão presentes"""
        condition = Text.contains("banco", "brasil")
        assert condition.matches(Transaction("Banco do Brasil", 100))

    def test_contains_not_all_terms_present(self):
        """Testa quando nem todos os termos estão presentes"""
        condition = Text.contains("banco", "brasil")
        assert not condition.matches(Transaction("Banco Itau", 100))
        assert not condition.matches(Transaction("Brasil", 100))

    def test_contains_case_insensitive_default(self):
        """Testa case insensitivity por padrão"""
        condition = Text.contains("banco")
        assert condition.matches(Transaction("BANCO", 100))
        assert condition.matches(Transaction("banco", 100))
        assert condition.matches(Transaction("BaNcO", 100))

    def test_contains_case_sensitive(self):
        """Testa case sensitivity quando ativado"""
        condition = Text.contains("Banco", case_sensitive=True)
        assert condition.matches(Transaction("Banco do Brasil", 100))
        assert not condition.matches(Transaction("BANCO DO BRASIL", 100))
        assert not condition.matches(Transaction("banco do brasil", 100))

    def test_contains_empty_terms_raises_error(self):
        """Testa que fornecer termos vazios lança erro"""
        with pytest.raises(ValueError):
            Text.contains()

    def test_contains_describe(self):
        """Testa o método describe()"""
        condition = Text.contains("banco", "brasil")
        description = condition.describe()
        assert "banco" in description
        assert "brasil" in description
        assert "AND" in description


class TestTextAnyOf:
    """Testes para Text.any_of()"""

    def test_any_of_one_term_present(self):
        """Testa quando pelo menos um termo está presente"""
        condition = Text.any_of("cri", "deb", "lci")
        assert condition.matches(Transaction("Rendimento CRI", 100))
        assert condition.matches(Transaction("Amortização DEB", 100))
        assert condition.matches(Transaction("LCI Banco", 100))

    def test_any_of_no_term_present(self):
        """Testa quando nenhum termo está presente"""
        condition = Text.any_of("cri", "deb", "lci")
        assert not condition.matches(Transaction("Dividendos", 100))

    def test_any_of_describe(self):
        """Testa o método describe()"""
        condition = Text.any_of("cri", "deb")
        description = condition.describe()
        assert "cri" in description
        assert "deb" in description
        assert "OR" in description


class TestTextStartsWith:
    """Testes para Text.starts_with()"""

    def test_starts_with_match(self):
        """Testa quando o texto começa com um dos termos"""
        condition = Text.starts_with("pix", "ted")
        assert condition.matches(Transaction("PIX para João", -100))
        assert condition.matches(Transaction("TED Banco XYZ", -100))

    def test_starts_with_no_match(self):
        """Testa quando o texto não começa com nenhum termo"""
        condition = Text.starts_with("pix", "ted")
        assert not condition.matches(Transaction("Transferência PIX", -100))

    def test_starts_with_describe(self):
        """Testa o método describe()"""
        condition = Text.starts_with("pix")
        assert "starts with" in condition.describe()


class TestTextEndsWith:
    """Testes para Text.ends_with()"""

    def test_ends_with_match(self):
        """Testa quando o texto termina com um dos termos"""
        condition = Text.ends_with("mensais", "anuais")
        assert condition.matches(Transaction("Juros Mensais", 100))
        assert condition.matches(Transaction("Taxas Anuais", -50))

    def test_ends_with_no_match(self):
        """Testa quando o texto não termina com nenhum termo"""
        condition = Text.ends_with("mensais", "anuais")
        assert not condition.matches(Transaction("Mensais Juros", 100))

    def test_ends_with_describe(self):
        """Testa o método describe()"""
        condition = Text.ends_with("mensais")
        assert "ends with" in condition.describe()


class TestTextEquals:
    """Testes para Text.equals()"""

    def test_equals_exact_match(self):
        """Testa quando o texto é exatamente igual"""
        condition = Text.equals("pix")
        assert condition.matches(Transaction("PIX", -100))

    def test_equals_partial_match_fails(self):
        """Testa que match parcial não funciona"""
        condition = Text.equals("pix")
        assert not condition.matches(Transaction("PIX para João", -100))

    def test_equals_describe(self):
        """Testa o método describe()"""
        condition = Text.equals("pix")
        assert "equals" in condition.describe()
