"""
Claude Daemon Client - Wrapper para integrar el daemon en la CLI
Comunica con el servidor FastAPI via HTTP. Si no está disponible, gracefully degrada.
"""

import requests
import json
from typing import Dict, Optional, List, Any
from urllib.parse import urljoin
import os


class ClaudeDaemonClient:
    """Cliente HTTP para comunicar con el daemon."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, timeout: int = 5):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self._available = False
        self._check_availability()

    def _check_availability(self) -> bool:
        """Verifica si el daemon está disponible sin lanzar errores."""
        try:
            response = requests.get(
                f"{self.base_url}/health", timeout=self.timeout
            )
            self._available = response.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        """¿El daemon está disponible?"""
        return self._available

    def analyze_project(self, project_context: Dict) -> Optional[Dict]:
        """
        Analiza un proyecto usando los 5 ejes de validación.
        Si el daemon no está disponible, retorna None.
        """
        if not self._available:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/analyze/project",
                json=project_context,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (analyze): {e}")
            return None

    def check_card_completion(
        self,
        card_id: str,
        card_name: str,
        description: str = "",
        checklists: List[Dict] = None,
        comments: List[Dict] = None,
    ) -> Optional[Dict]:
        """
        Verifica si una tarjeta puede ser marcada como Done.
        Detecta fraude de completitud.
        """
        if not self._available:
            return None

        try:
            payload = {
                "card_id": card_id,
                "card_name": card_name,
                "description": description,
                "checklists": checklists or [],
                "comments": comments or [],
            }
            response = requests.post(
                f"{self.base_url}/fraud/check-completion",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (check_completion): {e}")
            return None

    def check_state_transition(
        self,
        card_id: str,
        from_state: str,
        to_state: str,
        board_cards: List[Dict] = None,
        history: List[Dict] = None,
    ) -> Optional[Dict]:
        """
        Verifica si un salto de estado es válido.
        Detecta transiciones inválidas y patrones de fraude.
        """
        if not self._available:
            return None

        try:
            payload = {
                "card_id": card_id,
                "from_state": from_state,
                "to_state": to_state,
                "board_cards": board_cards or [],
                "history": history or [],
            }
            response = requests.post(
                f"{self.base_url}/fraud/check-transition",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (check_transition): {e}")
            return None

    def check_duplication(
        self,
        card_name: str,
        board_cards: List[Dict],
        time_window_minutes: int = 60,
    ) -> Optional[Dict]:
        """
        Detecta tarjetas duplicadas.
        Si 3+ tarjetas similares en <60min, marca como fraude.
        """
        if not self._available:
            return None

        try:
            payload = {
                "card_name": card_name,
                "board_cards": board_cards,
                "time_window_minutes": time_window_minutes,
            }
            response = requests.post(
                f"{self.base_url}/fraud/check-duplication",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (check_duplication): {e}")
            return None

    def process_request(
        self,
        request_type: str,
        project_context: Dict,
        execution_data: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Procesa una solicitud a través del flujo completo:
        [Análisis] → [Recomendación] → [Confirmación] → [Ejecución]
        """
        if not self._available:
            return None

        try:
            payload = {
                "request_type": request_type,
                "project_context": project_context,
                "execution_data": execution_data or {},
            }
            response = requests.post(
                f"{self.base_url}/flow/process",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (process_request): {e}")
            return None

    def get_analysis_weights(self) -> Optional[Dict]:
        """Obtiene los pesos de los 5 ejes de análisis."""
        if not self._available:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/info/weights",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (get_weights): {e}")
            return None

    def get_fraud_rules(self) -> Optional[Dict]:
        """Obtiene las reglas de detección de fraude."""
        if not self._available:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/info/fraud-rules",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Claude Daemon error (get_fraud_rules): {e}")
            return None


# Función global para usar en la CLI
_daemon_client = None


def get_daemon_client() -> ClaudeDaemonClient:
    """Obtiene la instancia única del cliente daemon."""
    global _daemon_client
    if _daemon_client is None:
        _daemon_client = ClaudeDaemonClient()
    return _daemon_client


def is_daemon_available() -> bool:
    """¿El daemon está disponible?"""
    return get_daemon_client().is_available


# Decoradores para envolver comandos CLI con validación del daemon

def with_fraud_detection(check_type: str):
    """
    Decorator que añade detección de fraude a una operación CLI.
    check_type: "completion", "transition", "duplication"
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            client = get_daemon_client()
            if not client.is_available:
                # Si el daemon no está disponible, ejecuta normalmente
                return func(*args, **kwargs)

            # Aquí entra la lógica específica por tipo de check
            # (se expande según necesidad)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_project_analysis(func):
    """
    Decorator que envuelve una operación con análisis de proyecto.
    Útil para crear/mover tarjetas en bloque.
    """
    def wrapper(*args, **kwargs):
        client = get_daemon_client()
        if not client.is_available:
            return func(*args, **kwargs)

        # Obtener contexto del proyecto si está disponible
        # (normalmente desde board_id o project_context pasado)
        return func(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    # Test
    client = ClaudeDaemonClient()
    print(f"Daemon disponible: {client.is_available}")
    if client.is_available:
        weights = client.get_analysis_weights()
        print(f"Weights: {json.dumps(weights, indent=2)}")
