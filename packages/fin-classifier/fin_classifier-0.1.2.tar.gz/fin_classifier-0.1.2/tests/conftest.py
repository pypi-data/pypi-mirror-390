"""
Configuração global do pytest e fixtures reutilizáveis.

Este arquivo é carregado automaticamente pelo pytest e fornece
fixtures compartilhadas entre todos os testes.
"""

import pytest

from src.fin_classifier import Amount, BaseClassifier, ClassificationResult, Rule, Text, Transaction


# ===== FIXTURES GLOBAIS =====


@pytest.fixture
def sample_transactions() -> list[Transaction]:
    """Fixture com transações de exemplo para testes"""
    return [
        Transaction("Rendimento CRI XPTO Juros Mensais", 150.50),
        Transaction("Amortização DEB ABC Extraordinária", 1000.00),
        Transaction("TESOURO DIRETO SELIC 2029", 500.00),
        Transaction("Dividendos PETR4", 85.30),
        Transaction("Custo Operacional Escritório", -250.00),
        Transaction("Taxa Custódia Mensal", -15.00),
        Transaction("TAXA BOLSA B3", -10.50),
        Transaction("Imposto de Renda Retido", -45.20),
        Transaction("Transferência PIX para João", -300.00),
        Transaction("TED Banco XYZ", -150.00),
        Transaction("Aplicação CDB Liquidez Diária", -5000.00),
        Transaction("Aquisição LCI Banco ABC", -10000.00),
        Transaction("Resgate Fundo DI", 7500.00),
        Transaction("Venda Ações VALE3", 3200.00),
        Transaction("Pagamento Cartão de Crédito", -1500.00),
    ]


@pytest.fixture
def sample_transaction_single() -> Transaction:
    """Fixture com uma única transação para testes rápidos"""
    return Transaction("Rendimento CRI XPTO Juros", 150.50)


@pytest.fixture
def sample_transaction_negative() -> Transaction:
    """Fixture com uma transação negativa"""
    return Transaction("Custo Operacional", -250.00)


# ===== FIXTURES PARA CLASSIFICADORES =====


class SampleClassifier(BaseClassifier):
    """Classificador de exemplo para testes"""

    __ativo_juros = Rule(Text.any_of("cri", "deb", "lci", "lca") & Text.contains("juros") & Amount.positive())
    __ativo_amort = Rule(Text.any_of("cri", "deb", "lci", "lca") & Text.contains("amort") & Amount.positive())
    __tesouro_direto = Rule(Text.contains("tesouro", "direto") & Amount.positive())
    __dividendos = Rule(Text.any_of("dividendo", "jcp", "jscp") & Amount.positive())
    __despesas = Rule(Text.contains("custo") & ~Text.any_of("custodia", "oferta") & Amount.negative())
    __taxas_impostos = Rule(
        (Text.any_of("taxa", "imposto", "ir", "iof", "custodia") | Text.contains("taxa", "imposto")) & Amount.negative()
    )
    __transferencias = Rule(Text.any_of("transferencia", "pix", "ted", "doc") & Amount.negative())
    __aplicacoes = Rule(
        (Text.contains("aplicacao") | Text.contains("aquisicao") | Text.contains("compra")) & Amount.negative()
    )
    __resgates = Rule(
        (Text.contains("resgate") | Text.contains("venda") | Text.contains("liquidacao")) & Amount.positive()
    )
    __outros = Rule()


@pytest.fixture
def classifier():
    """Fixture com o classificador de exemplo"""
    return SampleClassifier


# ===== FIXTURES PARA CONDIÇÕES =====


@pytest.fixture
def text_condition_banco():
    """Fixture com uma condição de texto simples"""
    return Text.contains("banco")


@pytest.fixture
def amount_condition_positive():
    """Fixture com uma condição de valor positivo"""
    return Amount.positive()


@pytest.fixture
def combined_condition():
    """Fixture com uma condição combinada"""
    return Text.contains("banco") & Amount.positive()


# ===== HOOKS DO PYTEST =====


def pytest_configure(config):
    """Configuração global do pytest"""
    config.addinivalue_line("markers", "slow: marca testes como lentos (desselecionar com '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "unit: marca testes unitários")
    config.addinivalue_line("markers", "smoke: marca testes de smoke test")
