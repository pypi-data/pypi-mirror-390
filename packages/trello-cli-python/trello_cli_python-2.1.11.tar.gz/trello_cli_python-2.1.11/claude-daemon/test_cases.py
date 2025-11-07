"""
Test Cases - Validación de fraude y educación
Casos de uso realistas que demuestran cada aspecto del sistema.
"""

import json
from analyzer import ProjectAnalyzer
from fraud_detector import FraudDetector
from response_flow import ResponseFlowCoordinator


def test_analysis_good_project():
    """Caso 1: Proyecto bien definido - Debe pasar todos los ejes."""
    print("\n" + "=" * 80)
    print("TEST 1: Proyecto bien definido")
    print("=" * 80)

    analyzer = ProjectAnalyzer()

    context = {
        "description": "OAuth2 authentication system for e-commerce platform",
        "architecture": """
            Layers: Presentation (FastAPI REST), Business Logic (TokenService, UserService), Data Access (SQLAlchemy + PostgreSQL)
            Components: AuthController, TokenManager, CredentialValidator, UserRepository
            Data flow: Request → Middleware → Controller → Service → Repository → PostgreSQL DB
            Modules: auth, token, user, security
            Schemas: User entity, Token entity, RefreshToken entity
        """,
        "phases": """
            Phase 1 (MVP): 2 weeks
              - Login endpoint
              - Token refresh endpoint
              - Basic validation
            Phase 2 (R1): 1 week after MVP
              - 2FA implementation
              - Password reset flow
              - Rate limiting per IP
            Phase 3 (R2): Backlog
              - Social login integration
              - Multi-device management
        """,
        "timeline": "MVP: 2 weeks (weeks 1-2), R1: 1 week (week 3), R2: TBD (future quarters)",
        "dependencies": """
            Core: FastAPI 0.104, SQLAlchemy 2.0, python-jose 3.3.0, pydantic 2.5
            Database: PostgreSQL 14+, psycopg2 driver
            Security: bcrypt for password hashing, cryptography library
            Testing: pytest, pytest-asyncio, httpx
            Deployment: alembic for migrations, uvicorn ASGI server
            External APIs: None required for MVP
        """,
        "scope": """
            IN SCOPE (MVP):
            - User registration and login
            - JWT token generation and validation
            - Token refresh mechanism
            - Basic rate limiting
            - Input validation and sanitization
            - Password hashing with bcrypt
            - User session management
            - Comprehensive logging

            OUT OF SCOPE (R2):
            - Web UI (frontend team owns)
            - Email notifications
            - Social login providers
            - Mobile app specific flows
            - Multi-factor authentication (R1)
        """,
        "risks": """
            Risk 1 (CRITICAL): Token expiration and refresh race conditions
            - Impact: User sessions lost, potential security gaps
            - Mitigation: Implement atomic token rotation, handle concurrent requests
            - Assumption: PostgreSQL transactions are reliable

            Risk 2 (HIGH): SQL injection in user queries
            - Impact: Data breach, unauthorized access
            - Mitigation: Always use ORM, no raw SQL, parameterized queries

            Risk 3 (HIGH): Performance degradation under login spike
            - Impact: Service unavailability
            - Mitigation: Redis cache layer, horizontal scaling, load testing
            - Assumption: Can provision additional resources if needed

            Risk 4 (MEDIUM): Password reset token expiration handling
            - Impact: Users locked out of accounts
            - Mitigation: Implement secure token rotation, audit logging

            Technical Debt: None at MVP launch
        """,
    }

    result = analyzer.analyze(context)

    print(f"\nScore General: {result.overall_score:.0f}/100")
    print(f"Ejecutable: {result.is_executable}")
    print(f"Resumen: {result.summary}\n")

    for axis in result.axes:
        print(f"  {axis.axis.upper()}: {axis.score:.0f}/100 [{axis.level.value}]")
        if axis.issues:
            for issue in axis.issues:
                print(f"    - Issue: {issue}")
        if axis.suggestions:
            for sugg in axis.suggestions:
                print(f"    - Sugerencia: {sugg}")

    assert result.overall_score >= 70, "Debería tener score aceptable"
    assert result.is_executable, "Debería ser ejecutable"
    print("\n✅ TEST PASSED")


def test_analysis_poor_project():
    """Caso 2: Proyecto vago y caótico - Debe rechazar ejecución."""
    print("\n" + "=" * 80)
    print("TEST 2: Proyecto caótico (rechazo de ejecución)")
    print("=" * 80)

    analyzer = ProjectAnalyzer()

    context = {
        "description": "Hazme un Tiktok descentralizado con blockchain",
        "architecture": "",  # Vacío
        "phases": "",  # Sin fases
        "timeline": "Para ayer",
        "dependencies": "",  # Sin dependencias
        "scope": "Todo lo que existe en YouTube pero mejor",
        "risks": "",  # Sin riesgos documentados
    }

    result = analyzer.analyze(context)

    print(f"\nScore General: {result.overall_score:.0f}/100")
    print(f"Ejecutable: {result.is_executable}")
    print(f"Resumen: {result.summary}\n")

    print(f"Problemas críticos ({len(result.critical_issues)}):")
    for issue in result.critical_issues:
        print(f"  🚫 {issue}")

    assert result.overall_score < 50, "Debería tener score bajo"
    assert not result.is_executable, "Debería ser rechazado"
    print("\n✅ TEST PASSED (correctamente rechazado)")


def test_fraud_fake_completion():
    """Caso 3: Fraude - Marcar tarjeta Done sin completar checklists."""
    print("\n" + "=" * 80)
    print("TEST 3: Fraude - Fake completion (sin checklists)")
    print("=" * 80)

    fraud_detector = FraudDetector()

    card_data = {
        "id": "card_123",
        "name": "Implement OAuth2",
        "description": "Add token generation and refresh endpoints",
        "checklists": [
            {
                "name": "Implementation",
                "items": [
                    {"state": "complete", "name": "Setup FastAPI"},
                    {"state": "incomplete", "name": "Implement TokenService"},
                    {"state": "incomplete", "name": "Write tests"},
                    {"state": "incomplete", "name": "Setup PostgreSQL"},
                ],
            }
        ],
        "comments": [],
    }

    result = fraud_detector.check_card_completion(card_data)

    print(f"\nFraude detectado: {result.is_fraudulent}")
    print(f"Permite ejecución: {result.allows_execution}")
    print(f"Resumen: {result.summary}\n")

    for alert in result.alerts:
        print(f"  [{alert.level.value}] {alert.type}")
        print(f"    - {alert.message}")
        print(f"    - Evidencia: {alert.evidence}")
        print(f"    - Recomendación: {alert.recommendation}")

    assert result.is_fraudulent, "Debería detectar fraude"
    assert not result.allows_execution, "No debería permitir ejecución"
    print("\n✅ TEST PASSED")


def test_fraud_invalid_transition():
    """Caso 4: Fraude - Salto directo TODO -> DONE."""
    print("\n" + "=" * 80)
    print("TEST 4: Fraude - Salto inválido (TODO -> DONE)")
    print("=" * 80)

    fraud_detector = FraudDetector()

    result = fraud_detector.check_state_transition(
        card_id="card_456",
        from_state="To Do",
        to_state="Done",
        card_history=[],
    )

    print(f"\nFraude detectado: {result.is_fraudulent}")
    print(f"Permite ejecución: {result.allows_execution}")
    print(f"Resumen: {result.summary}\n")

    for alert in result.alerts:
        print(f"  [{alert.level.value}] {alert.type}")
        print(f"    - {alert.message}")
        print(f"    - Recomendación: {alert.recommendation}")

    assert result.is_fraudulent, "Debería detectar transición inválida"
    assert not result.allows_execution, "Debería bloquear ejecución"
    print("\n✅ TEST PASSED")


def test_fraud_duplication():
    """Caso 5: Fraude - Duplicación de tarjetas."""
    print("\n" + "=" * 80)
    print("TEST 5: Fraude - Duplicación (3+ tarjetas similares)")
    print("=" * 80)

    fraud_detector = FraudDetector()

    from datetime import datetime, timedelta

    now = datetime.now()
    recent_time = (now - timedelta(minutes=5)).isoformat()

    board_cards = [
        {"name": "Implement OAuth2 authentication", "id": "c1", "created_at": recent_time},
        {"name": "Implement OAuth2 auth system", "id": "c2", "created_at": (now - timedelta(minutes=3)).isoformat()},
        {"name": "OAuth2 authentication feature", "id": "c3", "created_at": (now - timedelta(minutes=1)).isoformat()},
        {"name": "Totally different task", "id": "c4", "created_at": (now - timedelta(hours=2)).isoformat()},
    ]

    result = fraud_detector.check_duplication(
        card_name="Implement OAuth2",
        board_cards=board_cards,
        time_window_minutes=60,
    )

    print(f"\nFraude detectado: {result.is_fraudulent}")
    print(f"Resumen: {result.summary}\n")

    for alert in result.alerts:
        print(f"  [{alert.level.value}] {alert.type}")
        print(f"    - {alert.message}")
        print(f"    - Recomendación: {alert.recommendation}")

    assert result.is_fraudulent, "Debería detectar duplicación"
    print("\n✅ TEST PASSED")


def test_full_flow_good():
    """Caso 6: Flujo completo - Proyecto bueno + operación válida."""
    print("\n" + "=" * 80)
    print("TEST 6: Flujo completo - Aprobación")
    print("=" * 80)

    analyzer = ProjectAnalyzer()
    fraud_detector = FraudDetector()
    coordinator = ResponseFlowCoordinator(analyzer, fraud_detector)

    context = {
        "description": "Simple login system",
        "architecture": "REST API with JWT, PostgreSQL",
        "phases": "MVP (2 weeks)",
        "dependencies": "FastAPI, SQLAlchemy, JWT",
        "scope": "Login, logout, token refresh",
        "risks": "Token expiration, SQL injection (mitigated with ORM)",
    }

    response = coordinator.process_user_request(
        request_type="create_cards",
        project_context=context,
        execution_data=None,
    )

    print(f"\nStage: {response.stage.value}")
    print(f"Aprobado: {response.is_approved}")
    print(f"Requiere confirmación: {response.requires_confirmation}")
    print(f"\nMensaje:\n{response.message}")

    if response.recommendations:
        print(f"\nRecomendaciones:")
        for rec in response.recommendations:
            print(f"  • {rec}")

    assert response.is_approved, "Debería ser aprobado"
    print("\n✅ TEST PASSED")


def test_full_flow_blocked():
    """Caso 7: Flujo completo - Proyecto caótico → Bloqueado."""
    print("\n" + "=" * 80)
    print("TEST 7: Flujo completo - Bloqueo")
    print("=" * 80)

    analyzer = ProjectAnalyzer()
    fraud_detector = FraudDetector()
    coordinator = ResponseFlowCoordinator(analyzer, fraud_detector)

    context = {
        "description": "AI-powered everything",
        "architecture": "",
        "phases": "",
        "dependencies": "",
        "scope": "",
        "risks": "",
    }

    response = coordinator.process_user_request(
        request_type="create_cards",
        project_context=context,
        execution_data=None,
    )

    print(f"\nStage: {response.stage.value}")
    print(f"Aprobado: {response.is_approved}")
    print(f"Razón de bloqueo: {response.blocked_reason}")
    print(f"\nMensaje:\n{response.message}")

    assert not response.is_approved, "Debería ser rechazado"
    assert response.stage.value == "blocked", "Debería estar en stage blocked"
    print("\n✅ TEST PASSED (correctamente bloqueado)")


def run_all_tests():
    """Ejecuta todos los test cases."""
    print("\n" + "=" * 80)
    print("CLAUDE DAEMON - TEST SUITE")
    print("=" * 80)

    tests = [
        ("Good Project Analysis", test_analysis_good_project),
        ("Poor Project Analysis", test_analysis_poor_project),
        ("Fake Completion Fraud", test_fraud_fake_completion),
        ("Invalid Transition Fraud", test_fraud_invalid_transition),
        ("Duplication Fraud", test_fraud_duplication),
        ("Full Flow Approval", test_full_flow_good),
        ("Full Flow Blocked", test_full_flow_blocked),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"RESULTADOS: {passed} passed, {failed} failed")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
