def ingresar_personas():
    nombres = []
    tiempos = []

    while True:
        print("\n--- INGRESAR PERSONA ---")
        nombre = input("Nombre: ")
        tiempo = int(input("Tiempo de atención (minutos): "))

        nombres.append(nombre)
        tiempos.append(tiempo)

        opcion = input("\n1. Agregar otra persona\n2. Continuar\nSeleccione: ")

        if opcion == "2":
            break

    return nombres, tiempos


def mostrar_gantt(nombres, tiempos):
    print("\n==================================")
    print("ORDEN DE ATENCIÓN - FIFO")
    print("==================================\n")

    tiempo_actual = 0

    for i in range(len(nombres)):
        nombre = nombres[i]
        tiempo = tiempos[i]

        print(nombre + " " + " " * tiempo_actual + "#" * tiempo)

        tiempo_actual = tiempo_actual + tiempo

    input("\nPresione ENTER para ver métricas...")


def mostrar_metricas(nombres, tiempos):
    print("\n==================================")
    print("MÉTRICAS")
    print("==================================\n")

    tiempo_actual = 0
    total_espera = 0
    total_sistema = 0

    for i in range(len(nombres)):
        nombre = nombres[i]
        tiempo = tiempos[i]

        tiempo_espera = tiempo_actual
        tiempo_sistema = tiempo_espera + tiempo

        total_espera = total_espera + tiempo_espera
        total_sistema = total_sistema + tiempo_sistema

        print("Persona:", nombre)
        print("Tiempo de espera:", tiempo_espera)
        print("Tiempo total en sistema:", tiempo_sistema)
        print()

        tiempo_actual = tiempo_actual + tiempo

    cantidad = len(nombres)

    promedio_espera = total_espera / cantidad
    promedio_sistema = total_sistema / cantidad

    print("Tiempo promedio de espera:", round(promedio_espera, 2))
    print("Tiempo promedio en sistema:", round(promedio_sistema, 2))



def main():
    print("==================================")
    print("   SIMULADOR DE FILA FIFO")
    print("==================================")

    nombres, tiempos = ingresar_personas()
    mostrar_gantt(nombres, tiempos)
    mostrar_metricas(nombres, tiempos)


main()