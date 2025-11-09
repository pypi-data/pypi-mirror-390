"""
Testes de integração do classificador.
"""

import pytest

from src.fin_classifier import Amount, BaseClassifier, Rule, Text, Transaction


@pytest.mark.integration
class TestClassifierIntegration:
    """Testes de integração do classificador completo"""

    def test_ativo_juros_classification(self, classifier):
        """Testa classificação de juros de ativos"""
        transactions = [
            Transaction("Rendimento CRI XPTO Juros", 150.50),
            Transaction("DEB ABC Juros Mensais", 200.00),
            Transaction("LCI Banco Juros", 75.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "ativo_juros"
            assert result.priority == 0

    def test_ativo_amort_classification(self, classifier):
        """Testa classificação de amortização"""
        transactions = [
            Transaction("Amortização CRI XPTO", 1000.00),
            Transaction("DEB ABC Amortização Extraordinária", 5000.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "ativo_amort"
            assert result.priority == 1

    def test_tesouro_direto_classification(self, classifier):
        """Testa classificação de Tesouro Direto"""
        transactions = [
            Transaction("TESOURO DIRETO SELIC 2029", 500.00),
            Transaction("Resgate Tesouro Direto IPCA", 10000.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "tesouro_direto"

    def test_dividendos_classification(self, classifier):
        """Testa classificação de dividendos"""
        transactions = [
            Transaction("Dividendos PETR4", 85.30),
            Transaction("JCP VALE3", 120.00),
            Transaction("JSCP Empresa XYZ", 50.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "dividendos"

    def test_despesas_classification(self, classifier):
        """Testa classificação de despesas"""
        transactions = [
            Transaction("Custo Operacional Escritório", -250.00),
            Transaction("Custo Administrativo", -100.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "despesas"

    def test_despesas_excludes_custodia(self, classifier):
        """Testa que despesas não incluem custódia"""
        trans = Transaction("Custo Custodia Mensal", -15.00)
        result = classifier.classify(trans)

        assert result.category != "despesas"
        # Deve ser classificado como taxas_impostos
        assert result.category == "taxas_impostos"

    def test_taxas_impostos_classification(self, classifier):
        """Testa classificação de taxas e impostos"""
        transactions = [
            Transaction("Taxa Custódia", -15.00),
            Transaction("TAXA BOLSA B3", -10.50),
            Transaction("Imposto de Renda", -45.20),
            Transaction("IOF Operação", -5.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "taxas_impostos"

    def test_transferencias_classification(self, classifier):
        """Testa classificação de transferências"""
        transactions = [
            Transaction("Transferência PIX", -300.00),
            Transaction("TED Banco XYZ", -150.00),
            Transaction("DOC Pagamento", -200.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "transferencias"

    def test_aplicacoes_classification(self, classifier):
        """Testa classificação de aplicações"""
        transactions = [
            Transaction("Aplicacao CDB", -5000.00),
            Transaction("Aquisicao LCI", -10000.00),
            Transaction("Compra Acoes PETR4", -2000.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "aplicacoes"

    def test_resgates_classification(self, classifier):
        """Testa classificação de resgates"""
        transactions = [
            Transaction("Resgate Fundo DI", 7500.00),
            Transaction("Venda Acoes VALE3", 3200.00),
            Transaction("Liquidacao CDB", 10000.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "resgates"

    def test_outros_fallback(self, classifier):
        """Testa classificação fallback para transações não reconhecidas"""
        transactions = [
            Transaction("Pagamento Credito", -1500.00),
            Transaction("Gastos Supermercado", -250.00),
            Transaction("Deposito", 5000.00),
        ]

        for trans in transactions:
            result = classifier.classify(trans)
            assert result.category == "outros"

    def test_priority_order(self, classifier):
        """Testa que a ordem de prioridade é respeitada"""
        # Esta transação poderia ser "ativo_juros" ou "resgates"
        # Mas "ativo_juros" tem prioridade maior (0 vs 8)
        trans = Transaction("Rendimento CRI Juros Resgate", 1000.00)
        result = classifier.classify(trans)

        assert result.category == "ativo_juros"
        assert result.priority == 0

    def test_batch_classification(self, classifier, sample_transactions):
        """Testa classificação em lote"""
        results = classifier.classify_batch(sample_transactions)

        assert len(results) == len(sample_transactions)
        assert all(hasattr(r, "category") for r in results)
        assert all(hasattr(r, "priority") for r in results)

    def test_get_rules(self, classifier):
        """Testa obtenção de regras do classificador"""
        rules = classifier.get_rules()
        assert len(rules) > 0
        assert all(hasattr(r, "category") for r in rules)

    def test_describe_rules(self, classifier):
        """Testa descrição de todas as regras"""
        description = classifier.describe_rules()
        assert isinstance(description, str)
        assert "SampleClassifier" in description or "Classifier" in description
