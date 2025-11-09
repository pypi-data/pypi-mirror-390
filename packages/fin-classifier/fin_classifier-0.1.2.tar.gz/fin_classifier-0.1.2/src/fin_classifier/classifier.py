from __future__ import annotations

from typing import ClassVar

from .conditions import AlwaysTrue, Condition
from .models import ClassificationResult, Transaction


class Rule:
    """
    Representa uma regra de classificação.

    Uma regra combina uma ou mais condições que determinam se uma
    transação deve ser classificada em determinada categoria.
    """

    def __init__(self, condition: Condition | None = None):
        self.condition = condition if condition is not None else AlwaysTrue()
        self.category: str | None = None
        self.priority: int | None = None
        self._validated = False

    def matches(self, transaction: Transaction) -> bool:
        """Verifica se a transação atende à condição da regra"""
        try:
            return self.condition.matches(transaction)
        except Exception as e:  # noqa: BLE001
            # Log do erro mas não quebra o fluxo
            print(f"Erro ao avaliar regra {self.category}: {e}")
            return False

    def describe(self) -> str:
        """Retorna descrição legível da regra"""
        return f"Rule(category={self.category}, priority={self.priority}, condition={self.condition.describe()})"

    def validate(self) -> None:
        """Valida que a regra está propriamente configurada"""
        if self.category is None:
            msg = "Regra deve ter uma categoria definida"
            raise ValueError(msg)
        if self.priority is None:
            msg = "Regra deve ter uma prioridade definida"
            raise ValueError(msg)
        self._validated = True

    def __repr__(self) -> str:
        return f"Rule(category={self.category!r}, priority={self.priority})"


# ===== METACLASS =====


class ClassifierMeta(type):
    """
    Metaclass que:
    1. Identifica atributos que são Rules (prefixo __)
    2. Extrai nome da categoria do nome do atributo
    3. Atribui prioridade baseada na ordem de definição
    4. Cria lista ordenada de regras
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **_):
        rules: list[Rule] = []

        # Itera sobre atributos da classe
        for attr_name, attr_value in list(namespace.items()):
            # Identifica Rules com prefixo __
            if isinstance(attr_value, Rule) and attr_name.startswith("_" + name + "__"):
                # Extrai nome limpo (remove name mangling)
                clean_name = attr_name.split("__", 1)[1]

                # Configura a regra
                attr_value.category = clean_name
                attr_value.priority = len(rules)
                attr_value.validate()

                rules.append(attr_value)

        # Adiciona lista de regras ordenadas ao namespace
        namespace["_rules"] = rules

        # Cria a classe
        return super().__new__(mcs, name, bases, namespace)


# ===== BASE CLASSIFIER =====


class BaseClassifier(metaclass=ClassifierMeta):
    """
    Classe base para definir classificadores de transações.

    Para criar um classificador:
    1. Herde desta classe
    2. Defina regras como atributos privados (__nome_da_categoria)
    3. Use operadores &, |, ~ para compor condições

    Example:
        class MeuClassificador(BaseClassifier):
            __salario = Rule(
                Text.any_of("salario", "vencimento") & Amount.positive()
            )
            __despesa = Rule(
                Text.contains("custo") & Amount.negative()
            )

    """

    _rules: ClassVar[list[Rule]] = []

    @classmethod
    def classify(cls, transaction: Transaction) -> ClassificationResult:
        """
        Classifica uma transação baseada nas regras definidas.

        Args:
            transaction: Transação a ser classificada

        Returns:
            ClassificationResult com a categoria e metadados

        Raises:
            ValueError: Se não houver regras definidas

        """
        if not cls._rules:
            msg = f"{cls.__name__} não possui regras definidas"
            raise ValueError(msg)

        # Itera pelas regras em ordem de prioridade
        for rule in cls._rules:
            if rule.matches(transaction):
                return ClassificationResult(
                    category=rule.category,
                    priority=rule.priority,
                    rule_name=rule.category,
                    matched_conditions=[rule.condition.describe()],
                )

        # Fallback (não deveria acontecer se houver regra com AlwaysTrue)
        return ClassificationResult(
            category="não_classificado",
            priority=999,
            rule_name="fallback",
            confidence=0.0,
        )

    @classmethod
    def classify_batch(cls, transactions: list[Transaction]) -> list[ClassificationResult]:
        """Classifica múltiplas transações"""
        return [cls.classify(trans) for trans in transactions]

    @classmethod
    def get_rules(cls) -> list[Rule]:
        """Retorna lista de regras definidas"""
        return cls._rules.copy()

    @classmethod
    def describe_rules(cls) -> str:
        """Retorna descrição legível de todas as regras"""
        lines = [f"\n{cls.__name__} - Regras de Classificação:\n"]
        lines.append("=" * 80)

        for rule in cls._rules:
            lines.append(f"\nPrioridade {rule.priority}: {rule.category}")
            lines.append(f"  Condição: {rule.condition.describe()}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
