"""
Fraud Detection Module - Anti-fraude rules
Detecta: tarjetas falsas, saltos de estado, duplicación.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class FraudLevel(str, Enum):
    CRITICAL = "critical"  # Bloquea ejecución
    HIGH = "high"  # Grita y registra
    MEDIUM = "medium"  # Advierte pero permite
    LOW = "low"  # Info solamente


@dataclass
class FraudAlert:
    level: FraudLevel
    type: str  # "fake_completion", "invalid_transition", "duplication", etc
    card_id: Optional[str]
    message: str
    evidence: str  # Descripción técnica del por qué
    recommendation: str
    timestamp: str


@dataclass
class FraudCheckResult:
    is_fraudulent: bool
    alerts: List[FraudAlert]
    summary: str
    allows_execution: bool  # ¿Se ejecuta o no?


class FraudDetector:
    """
    Sistema de detección de fraude en operaciones Trello.
    Reglas concretas: fake completions, state skips, duplication.
    """

    def __init__(self):
        self.recent_operations = []  # Registro de operaciones para detección de patrones

    def check_card_completion(
        self, card_data: Dict, board_history: Optional[List[Dict]] = None
    ) -> FraudCheckResult:
        """
        Verifica si una tarjeta a "Done" tiene evidencia real.
        Regla: Requiere N subtareas completadas O referencia a commit/PR.
        """
        alerts = []
        is_fraudulent = False

        card_name = card_data.get("name", "")
        card_desc = card_data.get("description", "")
        checklists = card_data.get("checklists", [])
        comments = card_data.get("comments", [])

        # Calcular completitud de subtareas
        total_items = 0
        completed_items = 0

        for checklist in checklists:
            items = checklist.get("items", [])
            for item in items:
                total_items += 1
                if item.get("state") == "complete":
                    completed_items += 1

        # Regla 1: Si hay checklists, requiere >= 70% completado
        if total_items > 0:
            completion_rate = completed_items / total_items
            if completion_rate < 0.7:
                is_fraudulent = True
                alerts.append(
                    FraudAlert(
                        level=FraudLevel.CRITICAL,
                        type="incomplete_checklists",
                        card_id=card_data.get("id"),
                        message=f"Tarjeta a 'Done' pero solo {completion_rate*100:.0f}% de subtareas completadas",
                        evidence=f"{completed_items}/{total_items} items completados",
                        recommendation="Completa las subtareas faltantes antes de marcar como Done",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        # Regla 2: Si no hay checklists, requiere evidencia en descripción/comentarios
        if total_items == 0:
            has_pr_reference = any(
                "pr" in text.lower() or "pull" in text.lower()
                for text in [card_name, card_desc]
            )
            has_commit_reference = any(
                "commit" in text.lower() or "merge" in text.lower()
                for text in [card_name, card_desc]
            )
            has_deployment = any(
                "deploy" in text.lower() or "release" in text.lower()
                for text in [card_name, card_desc]
            )

            if not (has_pr_reference or has_commit_reference or has_deployment):
                is_fraudulent = True
                alerts.append(
                    FraudAlert(
                        level=FraudLevel.HIGH,
                        type="no_completion_evidence",
                        card_id=card_data.get("id"),
                        message="Tarjeta a 'Done' sin subtareas ni evidencia en descripción",
                        evidence="No hay PR, commit, o deploy referenciad en la tarjeta",
                        recommendation="Agrega checklists o referencia a PR/commit/deployment",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        allows_execution = len([a for a in alerts if a.level == FraudLevel.CRITICAL]) == 0

        summary = (
            "Tarjeta con potencial fraude de completitud"
            if is_fraudulent
            else "Tarjeta con evidencia válida"
        )

        return FraudCheckResult(
            is_fraudulent=is_fraudulent,
            alerts=alerts,
            summary=summary,
            allows_execution=allows_execution,
        )

    def check_state_transition(
        self, card_id: str, from_state: str, to_state: str, card_history: List[Dict]
    ) -> FraudCheckResult:
        """
        Verifica si el salto de estado es válido.
        Regla: No permitir saltos directos de TODO -> DONE sin pasos intermedios.
        """
        alerts = []
        is_fraudulent = False

        valid_transitions = {
            "todo": ["in_progress", "blocked"],
            "in_progress": ["review", "testing", "done", "blocked"],
            "review": ["in_progress", "testing", "done"],
            "testing": ["done", "in_progress", "blocked"],
            "blocked": ["in_progress", "todo"],
            "done": [],  # No se puede salir de done
        }

        # Normalizar estados: "To Do" → "todo", "In Progress" → "in_progress", etc.
        from_normalized = from_state.lower().replace(" ", "_").replace("to_do", "todo")
        to_normalized = to_state.lower().replace(" ", "_").replace("to_do", "todo")

        # Obtener transiciones válidas
        allowed = valid_transitions.get(from_normalized, [])

        if to_normalized not in allowed:
            is_fraudulent = True

            # El salto TODO -> DONE es CRÍTICO
            level = FraudLevel.CRITICAL if (from_normalized == "todo" and to_normalized == "done") else FraudLevel.MEDIUM

            alerts.append(
                FraudAlert(
                    level=level,
                    type="invalid_transition",
                    card_id=card_id,
                    message=f"Transición inválida: {from_state} -> {to_state}",
                    evidence=f"Transición no permitida en flujo de trabajo estándar",
                    recommendation=f"Usa flujo válido: {from_state} -> {' o '.join(allowed)}",
                    timestamp=datetime.now().isoformat(),
                )
            )

        # Detectar patrón de saltos frecuentes (sin pasos intermedios)
        recent_skips = sum(
            1
            for op in self.recent_operations
            if op.get("type") == "invalid_transition"
            and (
                datetime.fromisoformat(op["timestamp"]) - datetime.now()
            ).days < 1
        )

        if recent_skips >= 3:
            is_fraudulent = True
            alerts.append(
                FraudAlert(
                    level=FraudLevel.HIGH,
                    type="pattern_state_skips",
                    card_id=card_id,
                    message=f"Patrón detectado: {recent_skips} saltos de estado en últimas 24h",
                    evidence="Múltiples transiciones inválidas en corto tiempo",
                    recommendation="Revisa el flujo de trabajo. ¿Hay automatización maliciosa?",
                    timestamp=datetime.now().isoformat(),
                )
            )

        # Bloquea si hay alertas CRITICAL o HIGH (para este caso)
        critical_or_high = [a for a in alerts if a.level in (FraudLevel.CRITICAL, FraudLevel.HIGH)]
        allows_execution = len(critical_or_high) == 0

        summary = "Transición sospechosa" if is_fraudulent else "Transición válida"

        return FraudCheckResult(
            is_fraudulent=is_fraudulent,
            alerts=alerts,
            summary=summary,
            allows_execution=allows_execution,
        )

    def check_duplication(
        self,
        card_name: str,
        board_cards: List[Dict],
        time_window_minutes: int = 60,
    ) -> FraudCheckResult:
        """
        Detecta tarjetas duplicadas por similitud de texto.
        Regla: Si 3+ tarjetas iguales en <60min, es probablemente fraude.
        """
        alerts = []
        is_fraudulent = False

        # Calcular similitud de texto simple (token overlap)
        card_tokens = set(card_name.lower().split())
        similar_cards = []

        for existing_card in board_cards:
            existing_tokens = set(existing_card.get("name", "").lower().split())

            # Calcular Jaccard similarity
            if len(card_tokens | existing_tokens) > 0:
                similarity = len(card_tokens & existing_tokens) / len(
                    card_tokens | existing_tokens
                )

                if similarity >= 0.33:  # 33% similar (detect when key tokens match: "OAuth2")
                    similar_cards.append(
                        {
                            "name": existing_card.get("name"),
                            "id": existing_card.get("id"),
                            "created_at": existing_card.get("created_at"),
                            "similarity": similarity,
                        }
                    )

        if len(similar_cards) >= 2:
            # Verificar si fueron creadas en tiempo_window
            now = datetime.now()
            recent_duplicates = []

            for dup in similar_cards:
                if dup.get("created_at"):
                    created = datetime.fromisoformat(dup["created_at"])
                    if (now - created).seconds < time_window_minutes * 60:
                        recent_duplicates.append(dup)

            if len(recent_duplicates) >= 2:
                is_fraudulent = True
                alerts.append(
                    FraudAlert(
                        level=FraudLevel.HIGH,
                        type="duplication",
                        card_id=None,
                        message=f"Duplicación detectada: {len(recent_duplicates)} tarjetas similares en {time_window_minutes} minutos",
                        evidence=f"Similitud: {', '.join(d['name'] for d in recent_duplicates)}",
                        recommendation="¿Quieres consolidar estas tarjetas? Puedo fusionarlas automáticamente.",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        allows_execution = not is_fraudulent

        summary = (
            f"Duplicación: {len(recent_duplicates)} tarjetas similares"
            if is_fraudulent
            else "Tarjeta única"
        )

        return FraudCheckResult(
            is_fraudulent=is_fraudulent,
            alerts=alerts,
            summary=summary,
            allows_execution=allows_execution,
        )

    def register_operation(self, operation: Dict):
        """Registra una operación para análisis de patrones."""
        operation["timestamp"] = datetime.now().isoformat()
        self.recent_operations.append(operation)

        # Mantener solo las últimas 1000 operaciones
        if len(self.recent_operations) > 1000:
            self.recent_operations = self.recent_operations[-1000:]

    def get_fraud_summary(self, alerts: List[FraudAlert]) -> str:
        """Genera un resumen educativo de alertas."""
        if not alerts:
            return "Sin alertas de fraude."

        critical_count = len([a for a in alerts if a.level == FraudLevel.CRITICAL])
        high_count = len([a for a in alerts if a.level == FraudLevel.HIGH])

        summary = f"Detectadas {len(alerts)} alertas: "
        if critical_count > 0:
            summary += f"{critical_count} críticas (bloqueo), "
        if high_count > 0:
            summary += f"{high_count} altas (grito)"

        return summary.rstrip(", ")
