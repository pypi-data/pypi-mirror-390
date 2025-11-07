"""
Ejemplos de integración del Claude Daemon en la CLI
Comandos nuevos: analyze-project, validate-card, validate-transition
"""

import sys
import json
from typing import Dict, List
from client import get_daemon_client, is_daemon_available


def format_analysis_report(analysis: Dict) -> str:
    """Formatea un reporte de análisis para mostrar en CLI."""
    if not analysis:
        return "❌ No se pudo obtener análisis (daemon no disponible)"

    output = []
    output.append("")
    output.append("=" * 80)
    output.append("📊 PROJECT ANALYSIS REPORT")
    output.append("=" * 80)
    output.append("")

    # Score general
    score = analysis.get("overall_score", 0)
    is_executable = analysis.get("is_executable", False)

    if score >= 80:
        status = "✅ EXCELENTE"
    elif score >= 60:
        status = "⚠️  VIABLE"
    elif score >= 40:
        status = "❌ RIESGOSO"
    else:
        status = "🚫 INCOHERENTE"

    output.append(f"Overall Score: {score:.0f}/100 [{status}]")
    output.append(f"Ejecutable: {'Sí ✅' if is_executable else 'No ❌'}")
    output.append("")
    output.append(f"Resumen: {analysis.get('summary', '')}")
    output.append("")

    # Detalles por eje
    axes = analysis.get("axes", [])
    output.append("─" * 80)
    output.append("VALIDACIÓN POR EJES:")
    output.append("─" * 80)

    for axis in axes:
        axis_name = axis.get("axis", "").upper()
        axis_score = axis.get("score", 0)
        axis_level = axis.get("level", "").upper()
        weight = axis.get("weight", 0)

        level_icon = {
            "CRITICAL": "🚫",
            "WARNING": "⚠️ ",
            "INFO": "ℹ️ ",
            "OK": "✅",
        }.get(axis_level, "❓")

        output.append(f"\n{level_icon} {axis_name} ({weight*100:.0f}% peso)")
        output.append(f"   Score: {axis_score:.0f}/100")

        issues = axis.get("issues", [])
        if issues:
            output.append("   Issues:")
            for issue in issues:
                output.append(f"     • {issue}")

        suggestions = axis.get("suggestions", [])
        if suggestions:
            output.append("   Sugerencias:")
            for suggestion in suggestions:
                output.append(f"     • {suggestion}")

    # Problemas críticos
    critical = analysis.get("critical_issues", [])
    if critical:
        output.append("")
        output.append("─" * 80)
        output.append("PROBLEMAS CRÍTICOS:")
        output.append("─" * 80)
        for issue in critical:
            output.append(f"🚫 {issue}")

    output.append("")
    output.append("=" * 80)

    return "\n".join(output)


def format_fraud_alerts(fraud_check: Dict) -> str:
    """Formatea alertas de fraude para CLI."""
    if not fraud_check:
        return ""

    output = []
    alerts = fraud_check.get("alerts", [])

    if not alerts:
        return "✅ Sin alertas de fraude"

    output.append("")
    output.append("⚠️  FRAUD DETECTION ALERTS:")
    output.append("─" * 60)

    for alert in alerts:
        level = alert.get("level", "").upper()
        alert_type = alert.get("type", "").upper()
        message = alert.get("message", "")

        level_icon = {
            "CRITICAL": "🚫",
            "HIGH": "⛔",
            "MEDIUM": "⚠️ ",
            "LOW": "ℹ️ ",
        }.get(level, "❓")

        output.append(f"\n{level_icon} [{level}] {alert_type}")
        output.append(f"   {message}")

    output.append("")
    output.append("─" * 60)

    return "\n".join(output)


# ============================================================================
# NUEVOS COMANDOS PARA LA CLI
# ============================================================================


def cmd_analyze_project(description: str, architecture: str = "", phases: str = "",
                       dependencies: str = "", scope: str = "", risks: str = ""):
    """
    Analiza la integridad de un proyecto contra 5 ejes de validación.

    Uso: trello analyze-project "Tu descripción" --arch "capas" --phases "MVP, R1" ...
    """
    client = get_daemon_client()

    if not client.is_available:
        print("❌ Claude Daemon no está disponible")
        print("   Inicia el daemon: python -m claude_daemon.app")
        return

    project_context = {
        "description": description,
        "architecture": architecture,
        "phases": phases,
        "dependencies": dependencies,
        "scope": scope,
        "risks": risks,
    }

    print("🔍 Analizando proyecto...")
    analysis = client.analyze_project(project_context)

    if not analysis or not analysis.get("success"):
        print("❌ Error al analizar proyecto")
        return

    print(format_analysis_report(analysis))


def cmd_validate_card_completion(card_id: str, card_name: str, description: str = ""):
    """
    Valida si una tarjeta puede ser marcada como Done.
    Detecta: checklists incompletos, falta de evidencia.

    Uso: trello validate-card-completion <card_id> "Nombre" [description]
    """
    client = get_daemon_client()

    if not client.is_available:
        print("❌ Claude Daemon no está disponible")
        return

    print(f"🔍 Validando tarjeta: {card_name}")
    fraud_check = client.check_card_completion(
        card_id=card_id,
        card_name=card_name,
        description=description,
    )

    if not fraud_check or not fraud_check.get("success"):
        print("❌ Error al validar tarjeta")
        return

    if fraud_check.get("is_fraudulent"):
        print(f"🚫 FRAUDE DETECTADO: {fraud_check.get('summary')}")
        print(format_fraud_alerts(fraud_check))
    else:
        print(f"✅ VÁLIDA: {fraud_check.get('summary')}")


def cmd_validate_transition(card_id: str, from_state: str, to_state: str):
    """
    Valida si una transición de estado es válida.
    Detecta: saltos inválidos (TODO->DONE), patrones de fraude.

    Uso: trello validate-transition <card_id> "To Do" "Done"
    """
    client = get_daemon_client()

    if not client.is_available:
        print("❌ Claude Daemon no está disponible")
        return

    print(f"🔍 Validando transición: {from_state} → {to_state}")
    fraud_check = client.check_state_transition(
        card_id=card_id,
        from_state=from_state,
        to_state=to_state,
    )

    if not fraud_check or not fraud_check.get("success"):
        print("❌ Error al validar transición")
        return

    if fraud_check.get("is_fraudulent"):
        print(f"🚫 TRANSICIÓN INVÁLIDA: {fraud_check.get('summary')}")
        print(format_fraud_alerts(fraud_check))
    else:
        print(f"✅ TRANSICIÓN VÁLIDA")


def cmd_daemon_status():
    """
    Muestra el estado del daemon y sus capacidades.

    Uso: trello daemon-status
    """
    client = get_daemon_client()

    print("")
    print("=" * 60)
    print("Claude Daemon Status")
    print("=" * 60)

    if client.is_available:
        print("✅ DAEMON DISPONIBLE")
        print("")
        print("Capacidades:")
        print("  • Análisis de contexto (5 ejes)")
        print("  • Detección de fraude (tarjetas, transiciones, duplicación)")
        print("  • Flujo de validación completo")
        print("")

        weights = client.get_analysis_weights()
        if weights:
            print("Pesos de análisis:")
            for axis, weight in weights.get("weights", {}).items():
                print(f"  • {axis}: {weight*100:.0f}%")
            print("")

        rules = client.get_fraud_rules()
        if rules:
            print("Reglas de fraude activas:")
            print("  • Card completion: Require 70% checklist + evidence")
            print("  • State transitions: Validate workflow paths")
            print("  • Duplication: Detect 2+ similar cards in 60min")

    else:
        print("❌ DAEMON NO DISPONIBLE")
        print("")
        print("Inicia el daemon:")
        print("  python -m claude_daemon.app")
        print("")
        print("O en background:")
        print("  nohup python -m claude_daemon.app > daemon.log 2>&1 &")

    print("")
    print("=" * 60)


if __name__ == "__main__":
    # Test
    if len(sys.argv) < 2:
        cmd_daemon_status()
    elif sys.argv[1] == "analyze":
        cmd_analyze_project("Test project", architecture="REST API")
    elif sys.argv[1] == "status":
        cmd_daemon_status()
