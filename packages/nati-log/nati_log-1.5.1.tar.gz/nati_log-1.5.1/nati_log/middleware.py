from .client import NatiLogClient

class NatiLogMiddleware:
    def __init__(self, get_response, api_url, api_url_login, app_id, username, password):
        """
        Middleware para registrar eventos automáticamente en NatiLog.
        """
        self.get_response = get_response

        # obtener parametros de settings
        self.api_url = getattr(settings, "NATILOG_API_URL", None)
        self.api_url_login = getattr(settings, "NATILOG_API_URL_LOGIN", None)
        self.app_id = getattr(settings, "NATILOG_APP_ID", None)
        self.username = getattr(settings, "NATILOG_USERNAME", None)
        self.password = getattr(settings, "NATILOG_PASSWORD", None)

        # inicializar el cliente
        self.natilog = NatiLogClient(
            api_url=api_url,
            api_url_login=api_url_login,
            app_id=app_id,
            username=username,
            password=password,
        )

    def __call__(self, request):
        response = self.get_response(request)

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

        return response