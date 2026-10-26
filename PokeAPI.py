"""Punto 3.2 - PokeAPI: casos 1, 2 y 3."""
from pathlib import Path

import pytest
import requests


URL_BASE = "https://pokeapi.co/api/v2"

# Valores esperados del caso 1 para comparar en el caso 2.
SIZE_BERRY_1 = 20
SOIL_DRYNESS_BERRY_1 = 15


def consultar_api(recurso):
    """Hace un GET, verifica HTTP 200 y devuelve el JSON."""
    url = f"{URL_BASE}/{recurso.strip('/')}/"
    print(f"\nGET {url}", flush=True)

    respuesta = requests.get(url, timeout=30)

    print(
        f"Código HTTP recibido: {respuesta.status_code}",
        flush=True,
    )

    assert respuesta.status_code == 200, (
        f"Se esperaba HTTP 200 y se obtuvo {respuesta.status_code}."
    )

    return respuesta.json()


def test_caso_1_berry_1():
    """Verifica los datos de berry/1."""
    print("\nINICIO DEL CASO 1 - BERRY/1", flush=True)

    datos = consultar_api("berry/1")

    # Verificar que size sea 20.
    print(f"size: {datos['size']} | Esperado: 20", flush=True)

    assert datos["size"] == SIZE_BERRY_1, (
        f"Se esperaba size=20 y se obtuvo {datos['size']}."
    )

    # Verificar que soil_dryness sea 15.
    print(
        f"soil_dryness: {datos['soil_dryness']} | Esperado: 15",
        flush=True,
    )

    assert datos["soil_dryness"] == SOIL_DRYNESS_BERRY_1, (
        f"Se esperaba soil_dryness=15 y se obtuvo {datos['soil_dryness']}."
    )

    # Verificar que firmness.name sea soft.
    print(
        f"firmness.name: {datos['firmness']['name']} | Esperado: soft",
        flush=True,
    )

    assert datos["firmness"]["name"] == "soft", (
        "Se esperaba firmness.name='soft' "
        f"y se obtuvo '{datos['firmness']['name']}'."
    )

    print("CASO 1 APROBADO.", flush=True)


def test_caso_2_berry_2():
    """Compara berry/2 con los valores esperados del caso 1."""
    print("\nINICIO DEL CASO 2 - BERRY/2", flush=True)

    datos = consultar_api("berry/2")

    # Verificar que firmness.name sea super-hard.
    print(
        f"firmness.name: {datos['firmness']['name']} | Esperado: super-hard",
        flush=True,
    )

    assert datos["firmness"]["name"] == "super-hard", (
        "Se esperaba firmness.name='super-hard' "
        f"y se obtuvo '{datos['firmness']['name']}'."
    )

    # Verificar que size sea mayor al del caso 1.
    print(
        f"size: {datos['size']} | Debe ser mayor que {SIZE_BERRY_1}",
        flush=True,
    )

    assert datos["size"] > SIZE_BERRY_1, (
        f"size debe ser mayor que {SIZE_BERRY_1}. "
        f"Se obtuvo: {datos['size']}."
    )

    # Verificar que soil_dryness sea igual al del caso 1.
    print(
        f"soil_dryness: {datos['soil_dryness']} "
        f"| Debe ser igual a {SOIL_DRYNESS_BERRY_1}",
        flush=True,
    )

    assert datos["soil_dryness"] == SOIL_DRYNESS_BERRY_1, (
        f"soil_dryness debe ser {SOIL_DRYNESS_BERRY_1}. "
        f"Se obtuvo: {datos['soil_dryness']}."
    )

    print("CASO 2 APROBADO.", flush=True)


def test_caso_3_pikachu():
    """Verifica la experiencia base y el tipo de Pikachu."""
    print("\nINICIO DEL CASO 3 - PIKACHU", flush=True)

    datos = consultar_api("pokemon/pikachu")

    # Verificar que la experiencia base sea mayor a 10 y menor a 1000.
    experiencia_base = datos["base_experience"]

    print(
        f"Experiencia base: {experiencia_base} "
        "| Debe ser mayor a 10 y menor a 1000",
        flush=True,
    )

    assert 10 < experiencia_base < 1000, (
        "La experiencia base debe ser mayor a 10 y menor a 1000. "
        f"Se obtuvo: {experiencia_base}."
    )

    # Verificar que su tipo sea electric.
    tipos = [elemento["type"]["name"] for elemento in datos["types"]]

    print(f"Tipos: {tipos} | Debe incluir electric", flush=True)

    assert "electric" in tipos, (
        f"Pikachu debe ser de tipo 'electric'. Tipos obtenidos: {tipos}."
    )

    print("CASO 3 APROBADO.", flush=True)


if __name__ == "__main__":
    archivo = Path(__file__).resolve()
    reporte = archivo.with_name("ReportePokeAPI.html")

    print(f"\nArchivo que se ejecutará: {archivo}", flush=True)
    print("Se ejecutarán los tres casos de PokeAPI.", flush=True)
    print(f"El reporte se guardará en: {reporte}", flush=True)

    # Ejecuta los tres casos y genera un único reporte HTML.
    raise SystemExit(
        pytest.main([
            str(archivo),
            "-vv",
            "--import-mode=importlib",
            "--capture=tee-sys",
            f"--html={reporte}",
            "--self-contained-html",
        ])
    )
