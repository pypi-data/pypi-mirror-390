"""
Context Analysis Module - 5 Ejes de Validación
Pesa cada eje y genera un score de integridad del proyecto.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    OK = "ok"


@dataclass
class AxisResult:
    axis: str
    score: float  # 0-100
    weight: float  # porcentaje del score total
    level: ValidationLevel
    issues: List[str]
    suggestions: List[str]


@dataclass
class AnalysisResult:
    overall_score: float  # 0-100 ponderado
    axes: List[AxisResult]
    summary: str
    is_executable: bool  # ¿Se puede ejecutar o requiere cambios?
    critical_issues: List[str]


class ProjectAnalyzer:
    """
    Analiza la integridad de un proyecto usando 5 ejes de validación.
    Cada eje tiene un peso específico en el score final.
    """

    WEIGHTS = {
        "architecture": 0.25,
        "phases": 0.15,
        "dependencies": 0.20,
        "scope": 0.20,
        "risks": 0.20,
    }

    def __init__(self):
        self.weights = self.WEIGHTS

    def analyze(self, project_context: Dict) -> AnalysisResult:
        """
        Analiza el contexto del proyecto contra 5 ejes.
        Input: project_context con claves como description, scope, architecture, etc.
        """
        axes_results = []

        # Eje 1: Arquitectura definida (25%)
        arch_result = self._analyze_architecture(project_context)
        axes_results.append(arch_result)

        # Eje 2: Fases mapeadas (15%)
        phases_result = self._analyze_phases(project_context)
        axes_results.append(phases_result)

        # Eje 3: Dependencias explícitas (20%)
        deps_result = self._analyze_dependencies(project_context)
        axes_results.append(deps_result)

        # Eje 4: Scope realista (20%)
        scope_result = self._analyze_scope(project_context)
        axes_results.append(scope_result)

        # Eje 5: Riesgos documentados (20%)
        risks_result = self._analyze_risks(project_context)
        axes_results.append(risks_result)

        # Calcular score ponderado
        overall_score = sum(
            axis.score * self.weights[axis.axis] for axis in axes_results
        )

        # Determinar si es ejecutable
        critical_issues = []
        for axis in axes_results:
            if axis.level == ValidationLevel.CRITICAL:
                critical_issues.extend(axis.issues)

        is_executable = len(critical_issues) == 0

        summary = self._generate_summary(axes_results, overall_score)

        return AnalysisResult(
            overall_score=overall_score,
            axes=axes_results,
            summary=summary,
            is_executable=is_executable,
            critical_issues=critical_issues,
        )

    def _analyze_architecture(self, context: Dict) -> AxisResult:
        """Eje 1: ¿Hay capas claras, flujos, entidades, data flow?"""
        issues = []
        suggestions = []
        score = 100

        arch_text = context.get("architecture", "").lower()

        # Buscar indicadores positivos
        indicators = [
            "layers",
            "modules",
            "components",
            "api",
            "database",
            "schema",
            "entity",
            "data flow",
            "service",
            "controller",
            "repository",
        ]
        found_indicators = sum(
            1 for indicator in indicators if indicator in arch_text
        )
        indicators_count = found_indicators / len(indicators) * 100

        if indicators_count < 30:
            score -= 40
            issues.append("No hay indicios de capas o módulos definidos")
            suggestions.append(
                "Define capas: Presentation, Business Logic, Data Access"
            )

        elif indicators_count < 60:
            score -= 20
            issues.append("Arquitectura parcialmente definida")
            suggestions.append("Detalla los flujos entre componentes")

        if "diagram" not in arch_text and "flowchart" not in arch_text:
            score -= 15
            suggestions.append("Incluye diagramas de arquitectura (C4, flowchart)")

        level = (
            ValidationLevel.CRITICAL
            if score < 40
            else ValidationLevel.WARNING if score < 70 else ValidationLevel.OK
        )

        return AxisResult(
            axis="architecture",
            score=max(0, score),
            weight=self.weights["architecture"],
            level=level,
            issues=issues,
            suggestions=suggestions,
        )

    def _analyze_phases(self, context: Dict) -> AxisResult:
        """Eje 2: ¿Existe breakdown temporal de ejecución?"""
        issues = []
        suggestions = []
        score = 100

        phases_text = context.get("phases", "").lower()
        timeline = context.get("timeline", "").lower()

        # Buscar fases comunes
        phase_indicators = ["mvp", "phase", "sprint", "release", "milestone", "r1"]
        found_phases = sum(1 for p in phase_indicators if p in phases_text)

        if found_phases == 0:
            score -= 50
            issues.append("No hay fases definidas")
            suggestions.append("Define MVP, R1, R2... con fechas aproximadas")

        elif found_phases < 2:
            score -= 25
            issues.append("Pocas fases definidas")
            suggestions.append("Desgrana más: mínimo 3-4 hitos")

        # Verificar si hay timeline
        if not timeline or len(timeline) < 10:
            score -= 20
            issues.append("Timeline no especificado")
            suggestions.append("Estima duración por fase (MVP: 2 semanas, etc)")

        level = (
            ValidationLevel.CRITICAL
            if score < 40
            else ValidationLevel.WARNING if score < 70 else ValidationLevel.OK
        )

        return AxisResult(
            axis="phases",
            score=max(0, score),
            weight=self.weights["phases"],
            level=level,
            issues=issues,
            suggestions=suggestions,
        )

    def _analyze_dependencies(self, context: Dict) -> AxisResult:
        """Eje 3: ¿Se declaran APIs, módulos, env vars, external factors?"""
        issues = []
        suggestions = []
        score = 100

        deps_text = (
            context.get("dependencies", "")
            + " "
            + context.get("external", "")
            + " "
            + context.get("integrations", "")
        ).lower()

        if len(deps_text.strip()) < 10:
            score -= 50
            issues.append("No hay dependencias documentadas")
            suggestions.append(
                "Lista: librerías, APIs externas, env vars, servicios"
            )

        # Buscar indicadores de dependencias comunes
        dep_indicators = [
            "api",
            "database",
            "auth",
            "payment",
            "email",
            "cache",
            "queue",
            "storage",
            "library",
            "framework",
        ]
        found_deps = sum(1 for d in dep_indicators if d in deps_text)

        if found_deps < 2:
            score -= 30
            issues.append("Pocas dependencias explícitas")
            suggestions.append("Declara qué librerías, servicios y APIs se usarán")

        # Verificar si hay versionado
        if "version" not in deps_text:
            score -= 15
            suggestions.append("Especifica versiones de dependencias críticas")

        level = (
            ValidationLevel.CRITICAL
            if score < 40
            else ValidationLevel.WARNING if score < 70 else ValidationLevel.OK
        )

        return AxisResult(
            axis="dependencies",
            score=max(0, score),
            weight=self.weights["dependencies"],
            level=level,
            issues=issues,
            suggestions=suggestions,
        )

    def _analyze_scope(self, context: Dict) -> AxisResult:
        """Eje 4: ¿Hay delirio? ¿Overengineering o simplismo?"""
        issues = []
        suggestions = []
        score = 100

        description = context.get("description", "").lower()
        scope = context.get("scope", "").lower()
        full_text = description + " " + scope

        # Detectar delirio: promesas imposibles
        red_flags = [
            ("tiktok clone", "decentralized tiktok", "tinder web3"),
            ("in 2 days",),
            ("no testing needed",),
            ("unlimited scale",),
            ("zero downtime",),
        ]

        for flags in red_flags:
            if any(flag in full_text for flag in flags):
                score -= 30
                issues.append(f"Delirio detectado: {flags[0]}")

        # Detectar simplismo: scope demasiado vago
        if len(scope) < 50:
            score -= 25
            issues.append("Scope demasiado vago")
            suggestions.append("Define: qué incluye, qué NO incluye, MVP vs. futuro")

        # Detectar overengineering: complejidad innecesaria
        overeng_indicators = ["kubernetes", "microservices", "distributed"]
        for indicator in overeng_indicators:
            if indicator in full_text and "startup" in description:
                score -= 20
                issues.append(f"Posible overengineering: {indicator}")

        # Chequear realismo de timeline
        timeline = context.get("timeline", "").lower()
        if "2 days" in timeline or "1 week" in timeline:
            if (
                "oauth" in full_text
                or "payment" in full_text
                or "analytics" in full_text
            ):
                score -= 25
                issues.append("Timeline poco realista para scope")
                suggestions.append(
                    "Reduce scope o extiende timeline (OAuth+payments: 3-4 semanas)"
                )

        level = (
            ValidationLevel.CRITICAL
            if score < 40
            else ValidationLevel.WARNING if score < 70 else ValidationLevel.OK
        )

        return AxisResult(
            axis="scope",
            score=max(0, score),
            weight=self.weights["scope"],
            level=level,
            issues=issues,
            suggestions=suggestions,
        )

    def _analyze_risks(self, context: Dict) -> AxisResult:
        """Eje 5: ¿Se reconocen cuellos de botella, deuda técnica, errores?"""
        issues = []
        suggestions = []
        score = 100

        risks_text = (
            context.get("risks", "")
            + " "
            + context.get("challenges", "")
            + " "
            + context.get("assumptions", "")
        ).lower()

        if len(risks_text.strip()) < 10:
            score -= 40
            issues.append("No hay riesgos documentados")
            suggestions.append(
                "Identifica: cuellos de botella, puntos críticos, deuda técnica"
            )

        # Buscar indicadores de risk awareness
        risk_indicators = [
            "risk",
            "bottleneck",
            "technical debt",
            "assumptions",
            "limitation",
            "challenge",
            "critical path",
        ]
        found_risks = sum(1 for r in risk_indicators if r in risks_text)

        if found_risks < 2:
            score -= 25
            issues.append("Riesgos insuficientemente documentados")
            suggestions.append(
                "Detalla: qué puede fallar, cuáles son puntos críticos, deudas técnicas"
            )

        # Si no hay plan de mitigación
        if "mitigation" not in risks_text and "plan" not in risks_text:
            score -= 15
            suggestions.append("Incluye planes de mitigación para riesgos críticos")

        level = (
            ValidationLevel.CRITICAL
            if score < 40
            else ValidationLevel.WARNING if score < 70 else ValidationLevel.OK
        )

        return AxisResult(
            axis="risks",
            score=max(0, score),
            weight=self.weights["risks"],
            level=level,
            issues=issues,
            suggestions=suggestions,
        )

    def _generate_summary(
        self, axes_results: List[AxisResult], overall_score: float
    ) -> str:
        """Genera un resumen educativo del análisis."""
        if overall_score >= 80:
            return "Proyecto sólido. Arquitectura clara, fases definidas, riesgos documentados. Procede con confianza."

        elif overall_score >= 60:
            return "Proyecto viable pero con puntos débiles. Recomienda mejoras antes de ejecución completa."

        elif overall_score >= 40:
            return "Proyecto riesgoso. Requiere correcciones significativas. No se recomienda ejecución inmediata."

        else:
            return "Proyecto incoherente. Rechaza ejecución hasta que se resuelvan problemas críticos."
