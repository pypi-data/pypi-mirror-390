"""
Claude Daemon - FastAPI Microservice
Servidor HTTP local que expone análisis, detección de fraude, y orquestación de flujos.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import uvicorn
from datetime import datetime

from analyzer import ProjectAnalyzer
from fraud_detector import FraudDetector
from response_flow import ResponseFlowCoordinator


# ============================================================================
# Pydantic Models para validación de entrada/salida
# ============================================================================


class ProjectContext(BaseModel):
    """Contexto del proyecto para análisis."""
    description: Optional[str] = ""
    architecture: Optional[str] = ""
    phases: Optional[str] = ""
    timeline: Optional[str] = ""
    dependencies: Optional[str] = ""
    external: Optional[str] = ""
    integrations: Optional[str] = ""
    scope: Optional[str] = ""
    risks: Optional[str] = ""
    challenges: Optional[str] = ""
    assumptions: Optional[str] = ""


class CardCompletionRequest(BaseModel):
    """Solicitud para verificar si una tarjeta puede ser marcada como Done."""
    card_id: str
    card_name: str
    description: Optional[str] = ""
    checklists: Optional[List[Dict]] = []
    comments: Optional[List[Dict]] = []


class CardTransitionRequest(BaseModel):
    """Solicitud para verificar si una transición de estado es válida."""
    card_id: str
    from_state: str
    to_state: str
    board_cards: Optional[List[Dict]] = []
    history: Optional[List[Dict]] = []


class CreateCardsRequest(BaseModel):
    """Solicitud para crear tarjetas (incluye contexto y datos de ejecución)."""
    project_context: ProjectContext
    cards_to_create: List[Dict]  # [{"name": "...", "list_id": "...", ...}]


class ProcessRequest(BaseModel):
    """Solicitud general de procesamiento."""
    request_type: str  # create_cards, move_card, complete_card, search_project
    project_context: ProjectContext
    execution_data: Optional[Dict] = None


# ============================================================================
# Inicialización del servidor FastAPI
# ============================================================================

app = FastAPI(
    title="Claude Daemon",
    description="AI-powered project analysis and Trello orchestration",
    version="1.0.0",
)

# Inicializar módulos
analyzer = ProjectAnalyzer()
fraud_detector = FraudDetector()
coordinator = ResponseFlowCoordinator(analyzer, fraud_detector)


# ============================================================================
# HEALTH CHECK
# ============================================================================


@app.get("/health")
def health_check():
    """Verifica que el daemon está corriendo."""
    return {
        "status": "ok",
        "service": "claude-daemon",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


# ============================================================================
# ENDPOINTS DE ANÁLISIS (5 EJES)
# ============================================================================


@app.post("/analyze/project")
def analyze_project(context: ProjectContext):
    """
    Analiza un proyecto contra los 5 ejes de validación.

    Retorna:
    - overall_score: 0-100 ponderado
    - axes: Resultados de cada eje con issues y suggestions
    - summary: Resumen educativo
    - is_executable: ¿Se puede ejecutar?
    """
    try:
        context_dict = context.dict()
        analysis = analyzer.analyze(context_dict)

        return {
            "success": True,
            "overall_score": analysis.overall_score,
            "is_executable": analysis.is_executable,
            "summary": analysis.summary,
            "critical_issues": analysis.critical_issues,
            "axes": [
                {
                    "axis": axis.axis,
                    "score": axis.score,
                    "weight": axis.weight,
                    "level": axis.level.value,
                    "issues": axis.issues,
                    "suggestions": axis.suggestions,
                }
                for axis in analysis.axes
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS DE DETECCIÓN DE FRAUDE
# ============================================================================


@app.post("/fraud/check-completion")
def check_card_completion(request: CardCompletionRequest):
    """
    Verifica si una tarjeta puede ser marcada como Done.
    Reglas: N subtareas completadas O evidencia de commit/PR/deployment.
    """
    try:
        card_data = {
            "id": request.card_id,
            "name": request.card_name,
            "description": request.description,
            "checklists": request.checklists or [],
            "comments": request.comments or [],
        }

        result = fraud_detector.check_card_completion(card_data)

        return {
            "success": True,
            "is_fraudulent": result.is_fraudulent,
            "allows_execution": result.allows_execution,
            "summary": result.summary,
            "alerts": [
                {
                    "level": alert.level.value,
                    "type": alert.type,
                    "message": alert.message,
                    "evidence": alert.evidence,
                    "recommendation": alert.recommendation,
                }
                for alert in result.alerts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fraud/check-transition")
def check_state_transition(request: CardTransitionRequest):
    """
    Verifica si un salto de estado es válido.
    Detecta: saltos directos TODO->DONE, patrones de skips.
    """
    try:
        result = fraud_detector.check_state_transition(
            request.card_id,
            request.from_state,
            request.to_state,
            request.history or [],
        )

        return {
            "success": True,
            "is_fraudulent": result.is_fraudulent,
            "allows_execution": result.allows_execution,
            "summary": result.summary,
            "alerts": [
                {
                    "level": alert.level.value,
                    "type": alert.type,
                    "message": alert.message,
                    "evidence": alert.evidence,
                    "recommendation": alert.recommendation,
                }
                for alert in result.alerts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fraud/check-duplication")
def check_card_duplication(request: Dict):
    """
    Detecta tarjetas duplicadas por similitud de texto.
    Si 3+ tarjetas iguales en <60min, marca como fraude.
    """
    try:
        card_name = request.get("card_name", "")
        board_cards = request.get("board_cards", [])
        time_window = request.get("time_window_minutes", 60)

        result = fraud_detector.check_duplication(card_name, board_cards, time_window)

        return {
            "success": True,
            "is_fraudulent": result.is_fraudulent,
            "allows_execution": result.allows_execution,
            "summary": result.summary,
            "alerts": [
                {
                    "level": alert.level.value,
                    "type": alert.type,
                    "message": alert.message,
                    "evidence": alert.evidence,
                    "recommendation": alert.recommendation,
                }
                for alert in result.alerts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS DE FLUJO COMPLETO
# ============================================================================


@app.post("/flow/process")
def process_request(request: ProcessRequest):
    """
    Procesa una solicitud del usuario a través del flujo completo:
    [Análisis] → [Recomendación] → [Confirmación] → [Ejecución]

    request_type: create_cards, move_card, complete_card, search_project
    """
    try:
        context_dict = request.project_context.dict()

        response = coordinator.process_user_request(
            request.request_type, context_dict, request.execution_data
        )

        return {
            "success": True,
            "stage": response.stage.value,
            "is_approved": response.is_approved,
            "message": response.message,
            "requires_confirmation": response.requires_confirmation,
            "next_action": response.next_action,
            "analysis": {
                "overall_score": response.analysis.overall_score if response.analysis else None,
                "summary": response.analysis.summary if response.analysis else None,
                "critical_issues": response.analysis.critical_issues if response.analysis else [],
            } if response.analysis else None,
            "fraud_alerts": [
                {
                    "level": alert.level.value,
                    "type": alert.type,
                    "message": alert.message,
                }
                for alert in (response.fraud_check.alerts if response.fraud_check else [])
            ],
            "recommendations": response.recommendations or [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flow/confirm")
def confirm_execution(data: Dict):
    """
    Confirma la ejecución después de la recomendación.
    El usuario ya vio las recomendaciones y confirma que quiere proceder.
    """
    try:
        user_confirmed = data.get("confirmed", False)

        # En una implementación real, se pasaría la respuesta anterior
        # Por ahora, retornamos un esquema simplificado
        return {
            "success": True,
            "message": "Ejecución confirmada. Procediendo con operación Trello...",
            "stage": "execution",
            "next_action": "wait_for_trello_response",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS DE INFORMACIÓN
# ============================================================================


@app.get("/info/weights")
def get_analysis_weights():
    """Retorna los pesos de los 5 ejes de análisis."""
    return {
        "weights": analyzer.weights,
        "total": sum(analyzer.weights.values()),
        "description": "Pesos normalizados para cálculo de score ponderado",
    }


@app.get("/info/fraud-rules")
def get_fraud_rules():
    """Retorna las reglas de detección de fraude."""
    return {
        "rules": {
            "card_completion": {
                "checklist_requirement": "≥70% de subtareas completadas",
                "evidence_requirement": "PR, commit, o deployment referenciados",
            },
            "state_transitions": {
                "valid_transitions": {
                    "todo": ["in_progress", "blocked"],
                    "in_progress": ["review", "testing", "done", "blocked"],
                    "review": ["in_progress", "testing", "done"],
                    "testing": ["done", "in_progress", "blocked"],
                    "blocked": ["in_progress", "todo"],
                },
                "invalid_pattern_threshold": 3,
                "pattern_window": "24 hours",
            },
            "duplication": {
                "similarity_threshold": 0.85,
                "min_duplicates": 2,
                "time_window": "60 minutes",
            },
        }
    }


# ============================================================================
# ERROR HANDLING
# ============================================================================


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "error_type": type(exc).__name__,
    }


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Al iniciar el daemon."""
    print("🚀 Claude Daemon iniciando...")
    print(f"   Análisis: 5 ejes de validación cargados")
    print(f"   Anti-fraude: Detección activada")
    print(f"   Flujo: [Análisis] → [Recomendación] → [Confirmación] → [Ejecución]")


@app.on_event("shutdown")
async def shutdown_event():
    """Al apagar el daemon."""
    print("🛑 Claude Daemon apagándose...")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
