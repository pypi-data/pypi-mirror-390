import requests
import datetime

class NatiLogClient:

    def __init__(self, api_url, api_url_login, app_id, username, password):
        self.api_url = api_url.rstrip("/")  # Saca la barra final si ya la tiene
        self.api_url_login = api_url_login
        self.app_id = app_id
        self.username = username
        self.password = password
        self.token = None
        self.get_natilog_token()

    def get_natilog_token(self):
        payload = {"username": self.username, "password": self.password}
        try:
            response = requests.post(self.api_url_login, json=payload, timeout=10)
            response.raise_for_status()  # Lanza un error si el código de estado no es 200
            data = response.json()
            self.token = data.get("access") or data.get("token")
        except requests.exceptions.RequestException as e:
            self.token = None

    def registrar_evento(self, tipo_evento, mensaje, datos=None, fecha=None):
        """
        Registra un evento en la API de NatiLog
        Args:
        tipo_evento: str - Tipo de evento (e.g., "critical", "error", "warning", "info")
        mensaje: str - Mensaje del evento
        datos: dict - Datos adicionales del evento (opcional)
        fecha: str - Fecha y hora del evento en formato ISO 8601 (opcional)
        Returns: dict - Respuesta de la API en formato JSON
        Raises: requests.exceptions.RequestException - Si hay un error en la solicitud

        """

        if fecha is None:
            fecha = datetime.datetime.now().isoformat()  # Fecha y hora actual en formato ISO 8601

        payload = {
            "aplicacion": self.app_id,
            "tipo_evento": tipo_evento,
            "mensaje": mensaje,
            "datos": datos or {},  # Datos adicionales, si no hay datos, envía un diccionario vacío
            "fecha": fecha,
        }
        headers = {
            "Content-Type": "application/json",}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.post(f"{self.api_url}/evento/", json=payload, headers=headers, timeout=5)  # Envía el evento a la API
        response.raise_for_status()  # Lanza un error si la respuesta no es 200 OK
        return response.json()  # Devuelve la respuesta en formato JSON

    def debug(self, mensaje, datos=None, fecha=None):
        """
        Registra un evento de tipo "debug"
        """
        return self.registrar_evento("debug", mensaje, datos, fecha)

    def error(self, mensaje, datos=None, fecha=None):
        """
        Registra un evento de tipo "error"

        """
        return self.registrar_evento("error", mensaje, datos, fecha)

    def warning(self, mensaje, datos=None, fecha=None):
        """
        Registra un evento de tipo "warning"

        """
        return self.registrar_evento("warning", mensaje, datos, fecha)

    def info(self, mensaje, datos=None, fecha=None):
        """
        Registra un evento de tipo "info"
        """
        return self.registrar_evento("info", mensaje, datos, fecha)
    
    def critical(self, mensaje, datos=None, fecha=None):
        """
        Registra un evento de tipo "critical"
        """
        return self.registrar_evento("critical", mensaje, datos, fecha)
