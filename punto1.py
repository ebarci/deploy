"""Verifica números primos hasta que el usuario escriba salir."""

while True:
    entrada = input(
        "Ingresá un número entero o 'salir' para terminar: "
    ).strip()

    if entrada.lower() == "salir":
        print("Programa finalizado.")
        break

    try:
        numero = int(entrada)
    except ValueError:
        print("Entrada inválida. Ingresá un número entero o 'salir'.")
        continue

    # Reiniciar el contador para cada número.
    divisores = 0

    # Buscar los divisores del número.
    for i in range(1, numero + 1):
        if numero % i == 0:
            divisores = divisores + 1

    # Verificar si es primo.
    if divisores == 2:
        print(numero, "es un número primo.")
    else:
        print(numero, "no es un número primo.")
