"""
Testes de integração dos métodos describe().
"""

import pytest

from src.fin_classifier import Amount, Text, Transaction


@pytest.mark.integration
class TestDescribe:
    """Testes dos métodos describe()"""

    def test_condition_describe(self):
        """Testa describe de condições"""
        condition = Text.contains("banco") & Amount.positive()
        description = condition.describe()

        assert "banco" in description
        assert "AND" in description
        assert ">" in description

    def test_rule_describe(self, classifier):
        """Testa describe de regras"""
        rules = classifier.get_rules()

        for rule in rules:
            description = rule.describe()
            assert rule.category in description
            assert str(rule.priority) in description

    def test_classifier_describe_rules(self, classifier):
        """Testa describe do classificador completo"""
        description = classifier.describe_rules()

        assert isinstance(description, str)
        assert len(description) > 0
        # Deve conter nomes das categorias
        assert "ativo_juros" in description or "categoria" in description.lower()

    def test_text_contains_describe(self):
        """Testa describe para Text.contains"""
        condition = Text.contains("banco", "brasil")
        assert "all" in condition.describe().lower() or "and" in condition.describe().lower()

    def test_text_any_of_describe(self):
        """Testa describe para Text.any_of"""
        condition = Text.any_of("cri", "deb")
        assert "any" in condition.describe().lower() or "or" in condition.describe().lower()

    def test_text_starts_with_describe(self):
        """Testa describe para Text.starts_with"""
        condition = Text.starts_with("pix")
        assert "starts" in condition.describe().lower()

    def test_text_ends_with_describe(self):
        """Testa describe para Text.ends_with"""
        condition = Text.ends_with("juros")
        assert "ends" in condition.describe().lower()

    def test_text_equals_describe(self):
        """Testa describe para Text.equals"""
        condition = Text.equals("pix")
        assert "equals" in condition.describe().lower()

    def test_amount_gt_describe(self):
        """Testa describe para Amount.gt"""
        condition = Amount.gt(100)
        description = condition.describe()
        assert ">" in description
        assert "100" in description

    def test_amount_lt_describe(self):
        """Testa describe para Amount.lt"""
        condition = Amount.lt(100)
        description = condition.describe()
        assert "<" in description
        assert "100" in description

    def test_amount_between_describe(self):
        """Testa describe para Amount.between"""
        condition = Amount.between(100, 1000)
        description = condition.describe()
        assert "between" in description.lower()
        assert "100" in description
        assert "1000" in description

    def test_amount_positive_describe(self):
        """Testa describe para Amount.positive"""
        condition = Amount.positive()
        description = condition.describe()
        assert "positive" in description.lower() or ">" in description

    def test_amount_negative_describe(self):
        """Testa describe para Amount.negative"""
        condition = Amount.negative()
        description = condition.describe()
        assert "negative" in description.lower() or "<" in description

    def test_complex_condition_describe(self):
        """Testa describe para condição complexa"""
        condition = Text.any_of("cri", "deb") & Text.contains("juros") & Amount.positive() & ~Text.contains("provisao")
        description = condition.describe()

        assert isinstance(description, str)
        assert len(description) > 0
        assert "AND" in description or "OR" in description
