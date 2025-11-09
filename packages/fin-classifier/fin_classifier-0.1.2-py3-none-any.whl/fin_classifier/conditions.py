from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .models import Transaction


class Condition(ABC):
    """
    Classe base abstrata para condições de matching.
    Suporta operadores & (AND), | (OR) e ~ (NOT) para composição.
    """

    @abstractmethod
    def matches(self, transaction: Transaction) -> bool:
        """
        Verifica se a transação atende a condição.

        Args:
            transaction: Transação a ser verificada

        Returns:
            True se a condição é atendida, False caso contrário

        """
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        """
        Retorna uma descrição legível da condição.
        Útil para debugging e logging.
        """
        raise NotImplementedError

    def __and__(self, other: Condition) -> AndCondition:
        """Operador & para combinar condições com AND lógico"""
        if not isinstance(other, Condition):
            msg = f"Cannot combine Condition with {type(other)}"
            raise TypeError(msg)
        return AndCondition(self, other)

    def __or__(self, other: Condition) -> OrCondition:
        """Operador | para combinar condições com OR lógico"""
        if not isinstance(other, Condition):
            msg = f"Cannot combine Condition with {type(other)}"
            raise TypeError(msg)
        return OrCondition(self, other)

    def __invert__(self) -> NotCondition:
        """Operador ~ para negação lógica"""
        return NotCondition(self)


# ===== LOGICAL OPERATORS =====


class AndCondition(Condition):
    """Condição composta que requer ambas subcondições sejam verdadeiras"""

    def __init__(self, left: Condition, right: Condition):
        self.left = left
        self.right = right

    def matches(self, transaction: Transaction) -> bool:
        return self.left.matches(transaction) and self.right.matches(transaction)

    def describe(self) -> str:
        return f"({self.left.describe()} AND {self.right.describe()})"


class OrCondition(Condition):
    """Condição composta que requer pelo menos uma subcondição seja verdadeira"""

    def __init__(self, left: Condition, right: Condition):
        self.left = left
        self.right = right

    def matches(self, transaction: Transaction) -> bool:
        return self.left.matches(transaction) or self.right.matches(transaction)

    def describe(self) -> str:
        return f"({self.left.describe()} OR {self.right.describe()})"


class NotCondition(Condition):
    """Condição que inverte o resultado de outra condição"""

    def __init__(self, condition: Condition):
        self.condition = condition

    def matches(self, transaction: Transaction) -> bool:
        return not self.condition.matches(transaction)

    def describe(self) -> str:
        return f"NOT ({self.condition.describe()})"


# ===== TEXT CONDITIONS =====


class TextCondition(Condition):
    """
    Condição base para verificações de texto.
    Case-insensitive por padrão.
    """

    def __init__(self, *terms: str, case_sensitive: bool = False):
        if not terms:
            msg = "Pelo menos um termo deve ser fornecido"
            raise ValueError(msg)

        self.terms = terms
        self.case_sensitive = case_sensitive

    def _normalize(self, text: str) -> str:
        """Normaliza texto para comparação"""
        return text if self.case_sensitive else text.lower()

    def _get_text(self, transaction: Transaction) -> str:
        """Extrai e normaliza texto da transação"""
        return self._normalize(transaction.description)


class TextContainsAll(TextCondition):
    """Verifica se o texto contém TODOS os termos especificados (AND)"""

    def matches(self, transaction: Transaction) -> bool:
        text = self._get_text(transaction)
        return all(self._normalize(term) in text for term in self.terms)

    def describe(self) -> str:
        terms_str = " AND ".join(f'"{t}"' for t in self.terms)
        return f"text contains all: {terms_str}"


class TextContainsAny(TextCondition):
    """Verifica se o texto contém PELO MENOS UM dos termos especificados (OR)"""

    def matches(self, transaction: Transaction) -> bool:
        text = self._get_text(transaction)
        return any(self._normalize(term) in text for term in self.terms)

    def describe(self) -> str:
        terms_str = " OR ".join(f'"{t}"' for t in self.terms)
        return f"text contains any: {terms_str}"


class TextStartsWith(TextCondition):
    """Verifica se o texto começa com algum dos termos especificados"""

    def matches(self, transaction: Transaction) -> bool:
        text = self._get_text(transaction)
        return any(text.startswith(self._normalize(term)) for term in self.terms)

    def describe(self) -> str:
        terms_str = " OR ".join(f'"{t}"' for t in self.terms)
        return f"text starts with: {terms_str}"


class TextEndsWith(TextCondition):
    """Verifica se o texto termina com algum dos termos especificados"""

    def matches(self, transaction: Transaction) -> bool:
        text = self._get_text(transaction)
        return any(text.endswith(self._normalize(term)) for term in self.terms)

    def describe(self) -> str:
        terms_str = " OR ".join(f'"{t}"' for t in self.terms)
        return f"text ends with: {terms_str}"


class TextEquals(TextCondition):
    """Verifica se o texto é exatamente igual a algum dos termos"""

    def matches(self, transaction: Transaction) -> bool:
        text = self._get_text(transaction)
        return any(text == self._normalize(term) for term in self.terms)

    def describe(self) -> str:
        terms_str = " OR ".join(f'"{t}"' for t in self.terms)
        return f"text equals: {terms_str}"


# ===== AMOUNT CONDITIONS =====


class AmountCondition(Condition):
    """Condição base para verificações de valor"""

    def __init__(self, value: float, op: Callable[[float, float], bool], op_name: str):
        self.value = value
        self.op = op
        self.op_name = op_name

    def matches(self, transaction: Transaction) -> bool:
        return self.op(transaction.amount, self.value)

    def describe(self) -> str:
        return f"amount {self.op_name} {self.value}"


class AmountGreaterThan(AmountCondition):
    """Verifica se o valor é maior que o especificado"""

    def __init__(self, value: float):
        super().__init__(value, operator.gt, ">")


class AmountLessThan(AmountCondition):
    """Verifica se o valor é menor que o especificado"""

    def __init__(self, value: float):
        super().__init__(value, operator.lt, "<")


class AmountGreaterOrEqual(AmountCondition):
    """Verifica se o valor é maior ou igual ao especificado"""

    def __init__(self, value: float):
        super().__init__(value, operator.ge, ">=")


class AmountLessOrEqual(AmountCondition):
    """Verifica se o valor é menor ou igual ao especificado"""

    def __init__(self, value: float):
        super().__init__(value, operator.le, "<=")


class AmountEquals(AmountCondition):
    """Verifica se o valor é exatamente igual ao especificado"""

    def __init__(self, value: float, tolerance: float = 0.01):
        self.tolerance = tolerance
        super().__init__(value, lambda a, b: abs(a - b) < tolerance, "==")

    def describe(self) -> str:
        return f"amount == {self.value} (±{self.tolerance})"


class AmountBetween(Condition):
    """Verifica se o valor está entre dois valores (inclusive)"""

    def __init__(self, min_value: float, max_value: float):
        if min_value > max_value:
            msg = "min_value deve ser menor ou igual a max_value"
            raise ValueError(msg)
        self.min_value = min_value
        self.max_value = max_value

    def matches(self, transaction: Transaction) -> bool:
        return self.min_value <= transaction.amount <= self.max_value

    def describe(self) -> str:
        return f"amount between {self.min_value} and {self.max_value}"


class AmountPositive(Condition):
    """Verifica se o valor é positivo"""

    def matches(self, transaction: Transaction) -> bool:
        return transaction.amount > 0

    def describe(self) -> str:
        return "amount > 0 (positive)"


class AmountNegative(Condition):
    """Verifica se o valor é negativo"""

    def matches(self, transaction: Transaction) -> bool:
        return transaction.amount < 0

    def describe(self) -> str:
        return "amount < 0 (negative)"


# ===== ALWAYS TRUE CONDITION =====


class AlwaysTrue(Condition):
    """Condição que sempre retorna True - útil para fallback"""

    def matches(self, _: Transaction) -> bool:
        return True

    def describe(self) -> str:
        return "always true (fallback)"


class Text:
    """Namespace para condições de texto"""

    @staticmethod
    def contains(*terms: str, case_sensitive: bool = False) -> TextContainsAll:
        """
        Verifica se o texto contém TODOS os termos (AND lógico).

        Example:
            Text.contains("banco", "brasil")  # Ambos devem estar presentes

        """
        return TextContainsAll(*terms, case_sensitive=case_sensitive)

    @staticmethod
    def any_of(*terms: str, case_sensitive: bool = False) -> TextContainsAny:
        """
        Verifica se o texto contém QUALQUER um dos termos (OR lógico).

        Example:
            Text.any_of("cri", "deb", "lci")  # Qualquer um deve estar presente

        """
        return TextContainsAny(*terms, case_sensitive=case_sensitive)

    @staticmethod
    def starts_with(*terms: str, case_sensitive: bool = False) -> TextStartsWith:
        """Verifica se o texto começa com algum dos termos"""
        return TextStartsWith(*terms, case_sensitive=case_sensitive)

    @staticmethod
    def ends_with(*terms: str, case_sensitive: bool = False) -> TextEndsWith:
        """Verifica se o texto termina com algum dos termos"""
        return TextEndsWith(*terms, case_sensitive=case_sensitive)

    @staticmethod
    def equals(*terms: str, case_sensitive: bool = False) -> TextEquals:
        """Verifica se o texto é exatamente igual a algum dos termos"""
        return TextEquals(*terms, case_sensitive=case_sensitive)


class Amount:
    """Namespace para condições de valor"""

    @staticmethod
    def gt(value: float) -> AmountGreaterThan:
        """Maior que (>)"""
        return AmountGreaterThan(value)

    @staticmethod
    def lt(value: float) -> AmountLessThan:
        """Menor que (<)"""
        return AmountLessThan(value)

    @staticmethod
    def gte(value: float) -> AmountGreaterOrEqual:
        """Maior ou igual (>=)"""
        return AmountGreaterOrEqual(value)

    @staticmethod
    def lte(value: float) -> AmountLessOrEqual:
        """Menor ou igual (<=)"""
        return AmountLessOrEqual(value)

    @staticmethod
    def eq(value: float, tolerance: float = 0.01) -> AmountEquals:
        """Igual (==) com tolerância"""
        return AmountEquals(value, tolerance)

    @staticmethod
    def between(min_value: float, max_value: float) -> AmountBetween:
        """Entre dois valores (inclusivo)"""
        return AmountBetween(min_value, max_value)

    @staticmethod
    def positive() -> AmountPositive:
        """Valor positivo (> 0)"""
        return AmountPositive()

    @staticmethod
    def negative() -> AmountNegative:
        """Valor negativo (< 0)"""
        return AmountNegative()
