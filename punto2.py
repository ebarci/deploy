"""Calcula raíces reales hasta que el usuario escriba salir."""

import math


def calcular_raices(a, b, c):
    """Devuelve las raíces reales o un mensaje si no pueden calcularse."""
    if a == 0:
        return "No es una ecuación cuadrática: a debe ser distinto de 0."

    discriminante = b ** 2 - 4 * a * c

    if discriminante > 0:
        raiz_1 = (-b + math.sqrt(discriminante)) / (2 * a)
        raiz_2 = (-b - math.sqrt(discriminante)) / (2 * a)
        return raiz_1, raiz_2

    if discriminante == 0:
        return -b / (2 * a)

    return "La ecuación no tiene raíces reales."


def pedir_valor(nombre_coeficiente):
    """Solicita un número o devuelve None si el usuario escribe salir."""
    while True:
        entrada = input(
            f"Ingresá el valor de {nombre_coeficiente} "
            "o 'salir' para terminar: "
        ).strip()

        if entrada.lower() == "salir":
            return None

        try:
            return float(entrada)
        except ValueError:
            print("Entrada inválida. Ingresá un número o 'salir'.")


while True:
    valor_a = pedir_valor("a")
    if valor_a is None:
        break

    valor_b = pedir_valor("b")
    if valor_b is None:
        break

    valor_c = pedir_valor("c")
    if valor_c is None:
        break

    resultado = calcular_raices(valor_a, valor_b, valor_c)
    print("Resultado:", resultado)
    print()

print("Programa finalizado.")
