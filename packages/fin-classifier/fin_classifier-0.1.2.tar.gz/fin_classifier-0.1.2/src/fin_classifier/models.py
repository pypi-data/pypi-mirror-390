from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Transaction:
    """Representa uma transação bancária"""

    description: str
    amount: float
    date: datetime | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validação básica"""
        if not isinstance(self.description, str):
            msg = "description deve ser string"
            raise TypeError(msg)
        if not isinstance(self.amount, (int, float)):
            msg = "amount deve ser numérico"
            raise TypeError(msg)


@dataclass
class ClassificationResult:
    """Resultado de uma classificação"""

    category: str
    priority: int
    rule_name: str
    confidence: float = 1.0
    matched_conditions: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.category} (prioridade: {self.priority}, regra: {self.rule_name})"
