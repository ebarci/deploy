"""Punto 3.1 - SauceDemo: tres casos y un único reporte HTML."""

import os
from pathlib import Path
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


URL = "https://www.saucedemo.com/"
PAUSA = 3
PAUSA_FINAL = 10
TIEMPO_ESPERA = 20


def pausar():
    """Permite observar los pasos cuando Chrome está visible."""
    if os.environ.get("HEADLESS") != "1":
        time.sleep(PAUSA)


def esperar(navegador):
    """Reintenta buscando elementos nuevos si la página cambia."""
    return WebDriverWait(
        navegador,
        TIEMPO_ESPERA,
        ignored_exceptions=(
            NoSuchElementException,
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ),
    )


def click(navegador, localizador):
    """Hace clic en un elemento disponible y permite observar el paso."""
    def intentar(driver):
        elemento = driver.find_element(*localizador)

        if not elemento.is_displayed() or not elemento.is_enabled():
            return False

        elemento.click()
        return True

    esperar(navegador).until(intentar)
    pausar()


def escribir(navegador, id_campo, valor):
    """Completa un campo y verifica el valor ingresado."""
    def intentar(driver):
        campo = driver.find_element(By.ID, id_campo)

        if not campo.is_displayed() or not campo.is_enabled():
            return False

        campo.clear()
        campo.send_keys(valor)
        return campo.get_attribute("value") == valor

    esperar(navegador).until(intentar)
    pausar()


def leer_textos(navegador, selector):
    """Espera y devuelve los textos de los elementos encontrados."""
    def leer(driver):
        textos = [
            elemento.text
            for elemento in driver.find_elements(By.CSS_SELECTOR, selector)
        ]
        return textos if textos and all(textos) else False

    return esperar(navegador).until(leer)


@pytest.fixture(name="navegador")
def preparar_navegador():
    """Cada caso usa un navegador nuevo y lo cierra al terminar."""
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--incognito")
    opciones.add_argument("--start-maximized")
    opciones.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"],
    )
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })

    # Permite ejecutar también en servidores sin pantalla.
    if os.environ.get("HEADLESS") == "1":
        opciones.add_argument("--headless=new")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.add_argument("--window-size=1440,1000")

    if os.environ.get("CHROME_BINARY"):
        opciones.binary_location = os.environ["CHROME_BINARY"]

    driver = webdriver.Chrome(options=opciones)

    try:
        driver.set_page_load_timeout(40)
        yield driver
    finally:
        if os.environ.get("HEADLESS") != "1":
            print(
                f"\nEl navegador se cerrará en {PAUSA_FINAL} segundos.",
                flush=True,
            )
            time.sleep(PAUSA_FINAL)

        driver.quit()


def iniciar_sesion(navegador):
    """Ingresa con standard_user y espera la carga del catálogo."""
    print("\nIngresando a SauceDemo como standard_user.", flush=True)

    navegador.get(URL)
    escribir(navegador, "user-name", "standard_user")
    escribir(navegador, "password", "secret_sauce")
    click(navegador, (By.ID, "login-button"))

    esperar(navegador).until(
        EC.url_contains("inventory.html")
    )
    esperar(navegador).until(
        lambda driver: driver.find_elements(
            By.CSS_SELECTOR,
            ".inventory_item",
        )
    )

    print("Inicio de sesión correcto.", flush=True)


def leer_productos(navegador):
    """Obtiene los nombres y los identificadores de los productos."""
    def leer(driver):
        productos = driver.find_elements(
            By.CSS_SELECTOR,
            ".inventory_item",
        )

        if not productos:
            return False

        return [
            (
                producto.find_element(
                    By.CLASS_NAME,
                    "inventory_item_name",
                ).text,
                producto.find_element(
                    By.TAG_NAME,
                    "button",
                ).get_attribute("id"),
            )
            for producto in productos
        ]

    # Se guardan textos e identificadores, no elementos de la página.
    return esperar(navegador).until(leer)


def agregar_productos(navegador, cantidad=None):
    """Agrega los productos seleccionados y comprueba el contador."""
    productos = leer_productos(navegador)

    seleccionados = (
        productos if cantidad is None else productos[:cantidad]
    )

    if cantidad is not None:
        assert len(seleccionados) == cantidad, (
            "No hay suficientes productos."
        )

    for numero, (nombre, id_boton) in enumerate(
        seleccionados,
        start=1,
    ):
        print(f"Agregando al carrito: {nombre}", flush=True)

        click(navegador, (By.ID, id_boton))

        esperar(navegador).until(
            lambda driver, numero_actual=numero: driver.find_element(
                By.CLASS_NAME,
                "shopping_cart_badge",
            ).text == str(numero_actual)
        )

    return [nombre for nombre, _ in seleccionados]


def ir_al_carrito(navegador):
    """Abre el carrito y espera la página correspondiente."""
    print("Ingresando al carrito.", flush=True)

    click(navegador, (By.CLASS_NAME, "shopping_cart_link"))

    esperar(navegador).until(
        EC.url_contains("cart.html")
    )


def verificar_productos(navegador, esperados):
    """Comprueba que el carrito contenga los productos esperados."""
    encontrados = leer_textos(
        navegador,
        ".cart_item .inventory_item_name",
    )

    print(f"Productos esperados: {esperados}", flush=True)
    print(f"Productos encontrados: {encontrados}", flush=True)

    assert sorted(encontrados) == sorted(esperados), (
        f"Los productos no coinciden. Esperados: {esperados}. "
        f"Encontrados: {encontrados}."
    )


def verificar_error(navegador, esperado):
    """Verifica el mensaje de validación del checkout."""
    localizador = (By.CSS_SELECTOR, "[data-test='error']")

    esperar(navegador).until(
        EC.text_to_be_present_in_element(localizador, esperado),
        message=f"No apareció el mensaje: {esperado}",
    )

    mensaje = leer_textos(
        navegador,
        "[data-test='error']",
    )[0]

    print(f"Mensaje obtenido: {mensaje}", flush=True)

    assert mensaje == esperado, (
        f"Mensaje inesperado: {mensaje!r}"
    )

    pausar()


def leer_precios(navegador):
    """Obtiene los precios visibles y los convierte a números."""
    textos = [
        elemento.text.replace("$", "").strip()
        for elemento in navegador.find_elements(
            By.CLASS_NAME,
            "inventory_item_price",
        )
    ]

    if textos and all(textos):
        return [float(texto) for texto in textos]

    return []


def test_caso_1_ordenar_por_precio(navegador):
    """Ordenar por precio de menor a mayor y verificar el resultado."""
    print("\nCASO 1 - ORDENAR POR PRECIO", flush=True)

    iniciar_sesion(navegador)

    precios_antes = esperar(navegador).until(
        leer_precios
    )

    assert len(precios_antes) > 1, (
        "Se necesitan al menos dos productos."
    )

    precios_esperados = sorted(precios_antes)

    def seleccionar(driver):
        lista = driver.find_element(
            By.CLASS_NAME,
            "product_sort_container",
        )

        if lista.get_attribute("value") != "lohi":
            Select(lista).select_by_value("lohi")

        return driver.find_element(
            By.CLASS_NAME,
            "product_sort_container",
        ).get_attribute("value") == "lohi"

    print("Seleccionando Price (low to high).", flush=True)

    esperar(navegador).until(seleccionar)

    def orden_actualizado(driver):
        precios = leer_precios(driver)

        if len(precios) != len(precios_antes):
            return False

        if precios != precios_antes or precios_antes == precios_esperados:
            return precios

        return False

    precios_actuales = esperar(navegador).until(
        orden_actualizado
    )

    print(f"Precios antes: {precios_antes}", flush=True)
    print(f"Precios después: {precios_actuales}", flush=True)

    assert precios_actuales == precios_esperados, (
        f"Orden incorrecto. Esperado: {precios_esperados}. "
        f"Obtenido: {precios_actuales}."
    )

    pausar()
    print("CASO 1 APROBADO.", flush=True)


def test_caso_2_carrito_completo_y_errores(navegador):
    """Agregar todos los productos y verificar los campos obligatorios."""
    print(
        "\nCASO 2 - TODOS LOS PRODUCTOS Y ERRORES DEL CHECKOUT",
        flush=True,
    )

    iniciar_sesion(navegador)

    # Agregar todos los productos y verificar el carrito.
    esperados = agregar_productos(navegador)
    ir_al_carrito(navegador)
    verificar_productos(navegador, esperados)

    # Ir al checkout.
    click(navegador, (By.ID, "checkout"))

    esperar(navegador).until(
        EC.url_contains("checkout-step-one.html")
    )

    # Ingresar solamente el nombre.
    print("Ingresando solamente el nombre.", flush=True)

    escribir(navegador, "first-name", "Emanuel")

    assert navegador.find_element(
        By.ID,
        "last-name",
    ).get_attribute("value") == ""

    assert navegador.find_element(
        By.ID,
        "postal-code",
    ).get_attribute("value") == ""

    click(navegador, (By.ID, "continue"))

    # Verificar que el apellido sea obligatorio.
    verificar_error(
        navegador,
        "Error: Last Name is required",
    )

    # Ingresar el apellido y dejar vacío el código postal.
    print(
        "Ingresando el apellido y dejando vacío el código postal.",
        flush=True,
    )

    escribir(navegador, "last-name", "Prueba")

    assert navegador.find_element(
        By.ID,
        "postal-code",
    ).get_attribute("value") == ""

    click(navegador, (By.ID, "continue"))

    # Verificar que el código postal sea obligatorio.
    verificar_error(
        navegador,
        "Error: Postal Code is required",
    )

    assert "checkout-step-one.html" in navegador.current_url

    print("CASO 2 APROBADO.", flush=True)


def test_caso_3_remover_y_finalizar_compra(navegador):
    """Vaciar el carrito y luego comprar dos productos."""
    print(
        "\nCASO 3 - REMOVER UN PRODUCTO Y FINALIZAR UNA COMPRA",
        flush=True,
    )

    iniciar_sesion(navegador)

    # Agregar un producto e ingresar al carrito.
    primer_producto = agregar_productos(
        navegador,
        cantidad=1,
    )

    ir_al_carrito(navegador)
    verificar_productos(navegador, primer_producto)

    # Remover el producto.
    print("Removiendo el artículo.", flush=True)

    click(
        navegador,
        (By.CSS_SELECTOR, ".cart_item button[id^='remove-']"),
    )

    esperar(navegador).until(
        lambda driver: (
            not driver.find_elements(By.CLASS_NAME, "cart_item")
            and not driver.find_elements(
                By.CLASS_NAME,
                "shopping_cart_badge",
            )
        )
    )

    # Verificar que el carrito esté vacío.
    assert not navegador.find_elements(
        By.CLASS_NAME,
        "cart_item",
    )

    assert not navegador.find_elements(
        By.CLASS_NAME,
        "shopping_cart_badge",
    )

    print("Carrito vacío verificado.", flush=True)
    pausar()

    # Volver al catálogo.
    print("Seleccionando Continue Shopping.", flush=True)

    click(navegador, (By.ID, "continue-shopping"))

    esperar(navegador).until(
        EC.url_contains("inventory.html")
    )

    # Agregar dos productos y verificar el carrito.
    esperados = agregar_productos(
        navegador,
        cantidad=2,
    )

    ir_al_carrito(navegador)
    verificar_productos(navegador, esperados)

    # Hacer el checkout.
    print("Iniciando el checkout.", flush=True)

    click(navegador, (By.ID, "checkout"))

    esperar(navegador).until(
        EC.url_contains("checkout-step-one.html")
    )

    escribir(navegador, "first-name", "Emanuel")
    escribir(navegador, "last-name", "Prueba")
    escribir(navegador, "postal-code", "1000")

    click(navegador, (By.ID, "continue"))

    esperar(navegador).until(
        EC.url_contains("checkout-step-two.html")
    )

    verificar_productos(navegador, esperados)

    # Finalizar la compra.
    print("Finalizando la compra.", flush=True)

    click(navegador, (By.ID, "finish"))

    esperar(navegador).until(
        EC.url_contains("checkout-complete.html")
    )

    # Verificar que la compra fue realizada.
    mensaje = leer_textos(
        navegador,
        ".complete-header",
    )[0]

    assert mensaje == "Thank you for your order!", (
        f"No se confirmó la compra. Mensaje obtenido: {mensaje!r}"
    )

    print(f"Compra realizada: {mensaje}", flush=True)

    pausar()
    print("CASO 3 APROBADO.", flush=True)


if __name__ == "__main__":
    archivo = Path(__file__).resolve()
    reporte = archivo.with_name("ReporteSauceDemo.html")

    print(
        f"\nSe ejecutarán los tres casos de: {archivo}",
        flush=True,
    )
    print(f"El reporte se guardará en: {reporte}", flush=True)

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
