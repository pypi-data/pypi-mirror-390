from django.conf import settings
from .client import NatiLogClient

class NatiLogMiddleware:
    def __init__(self, get_response):
        """
        Middleware para registrar eventos automáticamente en NatiLog.
        """
        self.get_response = get_response
        print(f"NATILOG_API_URL: {getattr(settings, 'NATILOG_API_URL', None)}")
        print(f"NATILOG_USERNAME: {getattr(settings, 'NATILOG_USERNAME', None)}")

        # Obtener parámetros desde settings
        self.api_url = getattr(settings, "NATILOG_API_URL", None)
        self.api_url_login = getattr(settings, "NATILOG_API_URL_LOGIN", None)
        self.app_id = getattr(settings, "NATILOG_APP_ID", None)
        self.username = getattr(settings, "NATILOG_USERNAME", None)
        self.password = getattr(settings, "NATILOG_PASSWORD", None)

        # Inicializar el cliente con manejo de errores
        try:
            self.natilog = NatiLogClient(
                api_url=self.api_url,
                api_url_login=self.api_url_login,
                app_id=self.app_id,
                username=self.username,
                password=self.password,
            )
            print("NatiLogClient inicializado correctamente.")
        except Exception as e:
            print(f"Error al inicializar NatiLogClient: {e}")
            self.natilog = None

    def __call__(self, request):
        """
        Procesa la solicitud y registra eventos en NatiLog.
        """
        response = self.get_response(request)

        if self.natilog:
            try:
                # INFO: Cada request exitoso
                if 200 <= response.status_code < 300:
                    self.natilog.info(
                        f"Request OK: {request.method} {request.path}",
                        datos={"status_code": response.status_code}
                    )

                # WARNING: Redirecciones
                elif 300 <= response.status_code < 400:
                    self.natilog.warning(
                        f"Redirect: {request.method} {request.path}",
                        datos={"status_code": response.status_code}
                    )

                # ERROR: 404 y otros errores de cliente
                elif 400 <= response.status_code < 500:
                    self.natilog.error(
                        f"Client Error {response.status_code}: {request.method} {request.path}",
                        datos={"status_code": response.status_code}
                    )

                # CRITICAL: 500 y otros errores de servidor
                elif response.status_code >= 500:
                    self.natilog.critical(
                        f"Server Error {response.status_code}: {request.method} {request.path}",
                        datos={"status_code": response.status_code}
                    )
            except Exception as e:
                print(f"Error al registrar evento en NatiLog: {e}")

        return response