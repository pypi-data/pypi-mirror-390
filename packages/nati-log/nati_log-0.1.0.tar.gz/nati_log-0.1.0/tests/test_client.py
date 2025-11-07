import pytest
import requests
from nati_log.client import NatiLogClient

def test_registrar_evento_success(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear la respuesta de la API
    requests_mock.post(f"{api_url}/eventos", json={"status": "ok"}, status_code=201)

    resp = client.info("Prueba de evento", {"key": "value"})
    assert resp == {"status": "ok"}

def test_registrar_evento_error(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear error
    requests_mock.post(f"{api_url}/eventos", status_code=500)

    with pytest.raises(requests.exceptions.HTTPError):
        client.error("Algo falló")


def test_registrar_evento_timeout(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear timeout
    requests_mock.post(f"{api_url}/eventos", exc=requests.exceptions.Timeout)

    with pytest.raises(requests.exceptions.Timeout):
        client.warning("Esto tardó demasiado")


def test_registrar_evento_fecha_personalizada(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear la respuesta de la API
    requests_mock.post(f"{api_url}/eventos", json={"status": "ok"}, status_code=201)

    fecha_custom = "2024-01-01T12:00:00"
    resp = client.info("Evento con fecha personalizada", fecha=fecha_custom)
    assert resp == {"status": "ok"}

    # Verificar que la petición se hizo con la fecha correcta
    last_request = requests_mock.last_request
    assert last_request.json()["fecha"] == fecha_custom
    assert last_request.json()["aplicacion"] == "test-app"
    assert last_request.json()["tipo_evento"] == "info"
    assert last_request.json()["mensaje"] == "Evento con fecha personalizada"
    assert last_request.json()["datos"] == {}
    assert last_request.method == "POST"
    assert last_request.url == f"{api_url}/eventos"


def test_registrar_evento_sin_datos(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear la respuesta de la API
    requests_mock.post(f"{api_url}/eventos", json={"status": "ok"}, status_code=201)

    resp = client.info("Evento sin datos")
    assert resp == {"status": "ok"}

    # Verificar que la petición se hizo con datos como diccionario vacío
    last_request = requests_mock.last_request
    assert last_request.json()["datos"] == {}
    assert last_request.method == "POST"
    assert last_request.url == f"{api_url}/eventos"


def test_registrar_evento_con_datos(requests_mock):
    api_url = "http://fake-api"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear la respuesta de la API
    requests_mock.post(f"{api_url}/eventos", json={"status": "ok"}, status_code=201)

    datos_evento = {"user_id": 123, "action": "login"}
    resp = client.info("Evento con datos", datos=datos_evento)
    assert resp == {"status": "ok"}

    # Verificar que la petición se hizo con los datos correctos
    last_request = requests_mock.last_request
    assert last_request.json()["datos"] == datos_evento
    assert last_request.method == "POST"
    assert last_request.url == f"{api_url}/eventos"


def test_registrar_evento_app_name_con_barra_final(requests_mock):
    api_url = "http://fake-api/"
    client = NatiLogClient(api_url=api_url, app_name="test-app")

    # Mockear la respuesta de la API
    requests_mock.post(f"{api_url.rstrip('/')}/eventos", json={"status": "ok"}, status_code=201)

    resp = client.info("Prueba de evento con barra final en api_url")
    assert resp == {"status": "ok"}

    # Verificar que la petición se hizo correctamente
    last_request = requests_mock.last_request
    assert last_request.method == "POST"
    assert last_request.url == f"{api_url.rstrip('/')}/eventos"
