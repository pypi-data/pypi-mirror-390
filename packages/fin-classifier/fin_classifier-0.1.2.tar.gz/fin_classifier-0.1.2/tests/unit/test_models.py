"""
Testes unitários para modelos de dados.
"""

import pytest

from src.fin_classifier import ClassificationResult, Transaction


class TestTransaction:
    """Testes para o modelo Transaction"""

    def test_transaction_creation_valid(self):
        """Testa criação de transação válida"""
        trans = Transaction("Test Description", 100.50)
        assert trans.description == "Test Description"
        assert trans.amount == 100.50
        assert trans.date is None
        assert trans.metadata == {}

    def test_transaction_with_metadata(self):
        """Testa criação de transação com metadados"""
        metadata = {"source": "api", "id": 123}
        trans = Transaction("Test", 100, metadata=metadata)
        assert trans.metadata == metadata

    def test_transaction_invalid_description_type(self):
        """Testa que descrição deve ser string"""
        with pytest.raises(TypeError):
            Transaction(123, 100.00)  # type: ignore

    def test_transaction_invalid_amount_type_string(self):
        """Testa que valor deve ser numérico (rejeita string)"""
        with pytest.raises(TypeError):
            Transaction("Test", "100")  # type: ignore

    def test_transaction_invalid_amount_type_none(self):
        """Testa que valor não pode ser None"""
        with pytest.raises(TypeError):
            Transaction("Test", None)  # type: ignore

    def test_transaction_accepts_int_amount(self):
        """Testa que valor pode ser inteiro"""
        trans = Transaction("Test", 100)
        assert trans.amount == 100

    def test_transaction_accepts_float_amount(self):
        """Testa que valor pode ser float"""
        trans = Transaction("Test", 100.50)
        assert trans.amount == 100.50

    def test_transaction_negative_amount(self):
        """Testa que valor pode ser negativo"""
        trans = Transaction("Test", -100.50)
        assert trans.amount == -100.50

    def test_transaction_zero_amount(self):
        """Testa que valor pode ser zero"""
        trans = Transaction("Test", 0.0)
        assert trans.amount == 0.0


class TestClassificationResult:
    """Testes para o modelo ClassificationResult"""

    def test_classification_result_creation(self):
        """Testa criação de resultado de classificação"""
        result = ClassificationResult(category="salario", priority=0, rule_name="salario_rule")
        assert result.category == "salario"
        assert result.priority == 0
        assert result.rule_name == "salario_rule"
        assert result.confidence == 1.0
        assert result.matched_conditions == []

    def test_classification_result_with_confidence(self):
        """Testa resultado com confiança customizada"""
        result = ClassificationResult(category="salario", priority=0, rule_name="salario_rule", confidence=0.85)
        assert result.confidence == 0.85

    def test_classification_result_with_conditions(self):
        """Testa resultado com condições matched"""
        conditions = ["contains 'salario'", "amount > 0"]
        result = ClassificationResult(
            category="salario", priority=0, rule_name="salario_rule", matched_conditions=conditions
        )
        assert result.matched_conditions == conditions

    def test_classification_result_str_representation(self):
        """Testa representação em string do resultado"""
        result = ClassificationResult(category="salario", priority=0, rule_name="salario_rule")
        result_str = str(result)
        assert "salario" in result_str
        assert "0" in result_str
        assert "salario_rule" in result_str

    def test_classification_result_default_confidence(self):
        """Testa que confiança padrão é 1.0"""
        result = ClassificationResult(category="test", priority=0, rule_name="test_rule")
        assert result.confidence == 1.0

    def test_classification_result_default_matched_conditions(self):
        """Testa que matched_conditions padrão é lista vazia"""
        result = ClassificationResult(category="test", priority=0, rule_name="test_rule")
        assert result.matched_conditions == []
