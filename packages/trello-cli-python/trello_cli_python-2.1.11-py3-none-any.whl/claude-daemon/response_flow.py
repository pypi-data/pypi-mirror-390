"""
Response Flow Pipeline: [Análisis] → [Recomendación] → [Confirmación] → [Ejecución]
Coordinador de los ejes de validación y anti-fraude. Controla si se ejecuta o no.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from analyzer import AnalysisResult, ValidationLevel
from fraud_detector import FraudCheckResult, FraudLevel


class FlowStage(str, Enum):
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    CONFIRMATION = "confirmation"
    EXECUTION = "execution"
    BLOCKED = "blocked"


@dataclass
class FlowResponse:
    stage: FlowStage
    is_approved: bool
    message: str
    analysis: Optional[AnalysisResult] = None
    fraud_check: Optional[FraudCheckResult] = None
    recommendations: list = None
    requires_confirmation: bool = False
    blocked_reason: Optional[str] = None
    next_action: Optional[str] = None


class ResponseFlowCoordinator:
    """
    Orquesta el flujo completo: análisis, fraude, recomendaciones, confirmación.
    Decide si se ejecuta o se bloquea.
    """

    def __init__(self, analyzer, fraud_detector):
        self.analyzer = analyzer
        self.fraud_detector = fraud_detector

    def process_user_request(
        self, request_type: str, project_context: Dict, execution_data: Optional[Dict] = None
    ) -> FlowResponse:
        """
        Procesa una solicitud del usuario siguiendo el flujo completo.

        request_type: "create_cards", "move_card", "complete_card", "search_project"
        project_context: descripción del proyecto, arquitectura, etc.
        execution_data: datos específicos de la operación (card_id, list_id, etc.)
        """

        # Etapa 1: ANALYSIS (5 ejes de validación)
        analysis_result = self.analyzer.analyze(project_context)

        if not analysis_result.is_executable:
            return self._block_execution(
                f"Análisis rechaza ejecución. Crítica: {analysis_result.critical_issues}",
                analysis_result=analysis_result,
            )

        # Etapa 2: FRAUD CHECK
        fraud_result = None
        if request_type == "complete_card":
            fraud_result = self._check_card_fraud(execution_data)
        elif request_type == "move_card":
            fraud_result = self._check_transition_fraud(execution_data)
        elif request_type == "create_cards":
            fraud_result = self._check_duplication_fraud(execution_data)

        if fraud_result and not fraud_result.allows_execution:
            return self._block_execution(
                f"Fraude detectado: {fraud_result.summary}",
                analysis_result=analysis_result,
                fraud_check=fraud_result,
            )

        # Etapa 3: RECOMMENDATION
        recommendations = self._generate_recommendations(
            analysis_result, fraud_result, request_type
        )

        requires_confirmation = False
        if analysis_result.overall_score < 70:
            requires_confirmation = True

        # Etapa 4: CONFIRMATION / EXECUTION
        response = FlowResponse(
            stage=FlowStage.RECOMMENDATION,
            is_approved=True,
            message=f"Proyecto evaluado. Score: {analysis_result.overall_score:.0f}/100. {analysis_result.summary}",
            analysis=analysis_result,
            fraud_check=fraud_result,
            recommendations=recommendations,
            requires_confirmation=requires_confirmation,
            next_action="confirm" if requires_confirmation else "execute",
        )

        return response

    def confirm_and_execute(
        self, previous_response: FlowResponse, user_confirmed: bool = True
    ) -> FlowResponse:
        """
        Etapa 4: Confirmación y ejecución.
        Si el usuario confirma, se ejecuta. Si no, se cancela.
        """

        if not user_confirmed:
            return FlowResponse(
                stage=FlowStage.BLOCKED,
                is_approved=False,
                message="Ejecución cancelada por usuario",
                analysis=previous_response.analysis,
                blocked_reason="user_rejected",
            )

        # Aquí es donde entra la integración real con Trello
        return FlowResponse(
            stage=FlowStage.EXECUTION,
            is_approved=True,
            message="Ejecutando operación en Trello...",
            analysis=previous_response.analysis,
            next_action="wait_for_execution_result",
        )

    def _block_execution(
        self,
        reason: str,
        analysis_result: Optional[AnalysisResult] = None,
        fraud_check: Optional[FraudCheckResult] = None,
    ) -> FlowResponse:
        """Bloquea la ejecución con razón clara y educativa."""
        message = f"❌ BLOQUEADA: {reason}\n\n"

        if analysis_result and analysis_result.critical_issues:
            message += "Problemas críticos encontrados:\n"
            for issue in analysis_result.critical_issues:
                message += f"  • {issue}\n"

        if fraud_check and fraud_check.alerts:
            message += "\nAlertas de fraude:\n"
            for alert in fraud_check.alerts:
                message += f"  • [{alert.level}] {alert.message}\n"

        message += "\nProximos pasos:\n"
        message += "  1. Revisa la arquitectura del proyecto\n"
        message += "  2. Define fases y dependencias explícitamente\n"
        message += "  3. Documenta riesgos y mitigation plans\n"
        message += "  4. Reintenta cuando estés listo\n"

        return FlowResponse(
            stage=FlowStage.BLOCKED,
            is_approved=False,
            message=message,
            analysis=analysis_result,
            fraud_check=fraud_check,
            blocked_reason="critical_issues",
        )

    def _check_card_fraud(self, execution_data: Dict) -> Optional[FraudCheckResult]:
        """Verifica fraude al completar una tarjeta."""
        if not execution_data:
            return None

        return self.fraud_detector.check_card_completion(execution_data.get("card"))

    def _check_transition_fraud(
        self, execution_data: Dict
    ) -> Optional[FraudCheckResult]:
        """Verifica fraude al mover una tarjeta de estado."""
        if not execution_data:
            return None

        return self.fraud_detector.check_state_transition(
            execution_data.get("card_id"),
            execution_data.get("from_state"),
            execution_data.get("to_state"),
            execution_data.get("history", []),
        )

    def _check_duplication_fraud(
        self, execution_data: Dict
    ) -> Optional[FraudCheckResult]:
        """Verifica fraude por duplicación de tarjetas."""
        if not execution_data:
            return None

        return self.fraud_detector.check_duplication(
            execution_data.get("card_name"),
            execution_data.get("board_cards", []),
        )

    def _generate_recommendations(
        self,
        analysis: AnalysisResult,
        fraud: Optional[FraudCheckResult],
        request_type: str,
    ) -> list:
        """Genera recomendaciones basadas en análisis y fraude."""
        recommendations = []

        # Recomendaciones del análisis
        for axis in analysis.axes:
            if axis.level == ValidationLevel.WARNING:
                recommendations.extend(axis.suggestions)

        # Recomendaciones del fraude
        if fraud and fraud.alerts:
            for alert in fraud.alerts:
                recommendations.append(alert.recommendation)

        # Recomendación general según score
        if analysis.overall_score < 50:
            recommendations.insert(
                0, "⚠️ CRÍTICO: Proyecto muy incoherente. Requiere rediseño."
            )
        elif analysis.overall_score < 70:
            recommendations.insert(
                0, "⚠️ ADVERTENCIA: Proyecto tiene debilidades. Considera mejoras."
            )

        return recommendations[:5]  # Top 5 recommendations


# Ejemplo de uso (para testing)
if __name__ == "__main__":
    from analyzer import ProjectAnalyzer
    from fraud_detector import FraudDetector

    analyzer = ProjectAnalyzer()
    fraud_detector = FraudDetector()
    coordinator = ResponseFlowCoordinator(analyzer, fraud_detector)

    # Test context
    context = {
        "description": "Simple OAuth2 login system",
        "architecture": "REST API with JWT tokens, PostgreSQL database",
        "phases": "MVP (2 weeks), R1 (1 week)",
        "dependencies": "FastAPI, SQLAlchemy, python-jose, PostgreSQL",
        "scope": "Login, token refresh, logout",
        "risks": "Token expiration handling, SQL injection prevention",
    }

    response = coordinator.process_user_request("create_cards", context)
    print(f"Stage: {response.stage}")
    print(f"Approved: {response.is_approved}")
    print(f"Message: {response.message}")
