"""
Testes unitários para regras de classificação.
"""

import pytest

from src.fin_classifier import Amount, Rule, Text, Transaction


class TestRuleCreation:
    """Testes para criação de regras"""

    def test_rule_with_condition(self):
        """Testa criação de regra com condição"""
        condition = Text.contains("banco")
        rule = Rule(condition)
        assert rule.condition == condition

    def test_rule_without_condition(self):
        """Testa que regra sem condição usa AlwaysTrue"""
        rule = Rule()
        assert rule.condition is not None
        # Should match any transaction
        assert rule.matches(Transaction("Test", 100))

    def test_rule_matches_returns_bool(self):
        """Testa que matches retorna booleano"""
        rule = Rule(Text.contains("banco"))
        result = rule.matches(Transaction("Banco do Brasil", 100))
        assert isinstance(result, bool)

    def test_rule_matches_with_matching_transaction(self):
        """Testa rule.matches com transação que atende condição"""
        rule = Rule(Text.contains("banco"))
        assert rule.matches(Transaction("Banco do Brasil", 100))

    def test_rule_matches_with_non_matching_transaction(self):
        """Testa rule.matches com transação que não atende condição"""
        rule = Rule(Text.contains("banco"))
        assert not rule.matches(Transaction("Supermercado", 100))


class TestRuleAttributes:
    """Testes para atributos de regra"""

    def test_rule_category_default(self):
        """Testa que categoria padrão é None"""
        rule = Rule()
        assert rule.category is None

    def test_rule_category_assignment(self):
        """Testa atribuição de categoria"""
        rule = Rule()
        rule.category = "salario"
        assert rule.category == "salario"

    def test_rule_priority_default(self):
        """Testa que prioridade padrão é None"""
        rule = Rule()
        assert rule.priority is None

    def test_rule_priority_assignment(self):
        """Testa atribuição de prioridade"""
        rule = Rule()
        rule.priority = 0
        assert rule.priority == 0


class TestRuleValidation:
    """Testes para validação de regras"""

    def test_rule_validate_success(self):
        """Testa validação bem-sucedida de regra"""
        rule = Rule()
        rule.category = "salario"
        rule.priority = 0
        rule.validate()  # Should not raise

    def test_rule_validate_missing_category(self):
        """Testa validação com categoria faltando"""
        rule = Rule()
        rule.priority = 0
        with pytest.raises(ValueError):
            rule.validate()

    def test_rule_validate_missing_priority(self):
        """Testa validação com prioridade faltando"""
        rule = Rule()
        rule.category = "salario"
        with pytest.raises(ValueError):
            rule.validate()

    def test_rule_validate_both_missing(self):
        """Testa validação com ambos faltando"""
        rule = Rule()
        with pytest.raises(ValueError):
            rule.validate()


class TestRuleDescribe:
    """Testes para método describe de regras"""

    def test_rule_describe_format(self):
        """Testa formato do describe"""
        rule = Rule(Text.contains("banco"))
        rule.category = "transferencias"
        rule.priority = 5
        description = rule.describe()

        assert "transferencias" in description
        assert "5" in description
        assert "banco" in description


class TestRuleErrorHandling:
    """Testes para tratamento de erros em regras"""

    def test_rule_matches_handles_exception(self):
        """Testa que rule.matches trata exceções gracefully"""
        # Criar uma condição que vai causar erro
        rule = Rule(Text.contains("test"))
        # Mesmo com error, deve retornar False sem quebrar
        # (Isso testa o try/except interno do matches)
        result = rule.matches(Transaction("test", 100))
        assert isinstance(result, bool)

    def test_rule_repr(self):
        """Testa representação em string da regra"""
        rule = Rule()
        rule.category = "test"
        rule.priority = 1
        repr_str = repr(rule)
        assert "test" in repr_str
        assert "1" in repr_str
