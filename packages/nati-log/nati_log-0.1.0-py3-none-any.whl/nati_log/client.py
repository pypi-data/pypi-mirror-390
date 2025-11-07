import requests
import datetime

class NatiLogClient:
    
    def __init__(self, api_url, app_name):
        self.api_url = api_url.rstrip('/') # Saca la barra final si ya la tiene
        self.app_name = app_name


    def registrar_evento(self, tipo_evento, mensaje, datos=None, fecha=None):
        # diccionario con la información del evento
        
        if fecha is None:
            fecha = datetime.datetime.now().isoformat()  # Fecha y hora actual en formato ISO 8601

        payload = {
            "aplicacion": self.app_name,
            "tipo_evento": tipo_evento,
            "mensaje": mensaje,
            "datos": datos or {}, # Datos adicionales, si no hay datos, envía un diccionario vacío
            "fecha" : fecha
        }
        response = requests.post(f"{self.api_url}/eventos", json=payload, timeout=5) # Envía el evento a la API
        response.raise_for_status() # Lanza un error si la respuesta no es 200 OK
        return response.json() # Devuelve la respuesta en formato JSON
    

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