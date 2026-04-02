import time
import random

MEMORIA_RAM_TOTAL = 1000  # MB
memoria_en_uso = 0
archivo_log = "log_entrega_2.txt"

def guardar_log(mensaje):
    linea = f"[{time.strftime('%H:%M:%S')}] {mensaje}"
    with open(archivo_log, "a") as f:
        f.write(linea + "\n")
    print(linea)

def ingresar_personas():
    nombres = []
    tiempos = []
    memorias = [] 

    while True:
        print("\n--- INGRESAR PROCESO/PERSONA ---")
        nombre = input("Nombre del proceso: ")
        tiempo = int(input("Ciclos de CPU (Tiempo): "))
        memoria = int(input("Memoria requerida (MB): "))

        nombres.append(nombre)
        tiempos.append(tiempo)
        memorias.append(memoria)

        opcion = input("\n1. Agregar otro\n2. Continuar a ejecución\nSeleccione: ")
        if opcion == "2":
            break

    return nombres, tiempos, memorias

def ejecutar_simulacion(nombres, tiempos, memorias):
    global memoria_en_uso
    
    open(archivo_log, "w").close()
    guardar_log("=== INICIANDO EJECUCIÓN CON GESTIÓN DE MEMORIA ===")
    
    print("\n==================================")
    print("EJECUCIÓN EN TIEMPO REAL")
    print("==================================\n")

    for i in range(len(nombres)):
        nombre = nombres[i]
        cpu_necesario = tiempos[i]
        mem_necesaria = memorias[i]

        guardar_log(f"--- Siguiente: {nombre} (Pide {mem_necesaria}MB) ---")

        if (memoria_en_uso + mem_necesaria) <= MEMORIA_RAM_TOTAL:
            memoria_en_uso += mem_necesaria
            modo = "RAM"
            velocidad = 0.1
            guardar_log(f"ESTADO: {nombre} Esta siendo Atendido. Uso actual: {memoria_en_uso}/{MEMORIA_RAM_TOTAL}MB")
        else:
            modo = "SWAP (Disco)"
            velocidad = 0.5 
            guardar_log(f"ESTADO: {nombre} usa revision para ser atendido (LENTO)")

        for ciclo in range(1, cpu_necesario + 1):
            time.sleep(velocidad) 
            print(f" > {nombre}: Ejecutando {ciclo}/{cpu_necesario} en {modo}...")


        if modo == "RAM":
            memoria_en_uso -= mem_necesaria
            guardar_log(f"FINALIZADO: {nombre} liberó RAM. RAM Disponible: {MEMORIA_RAM_TOTAL - memoria_en_uso}MB")
        else:
            guardar_log(f"FINALIZADO: {nombre} terminó ejecución en SWAP.")

    input("\nEjecución terminada. Presione ENTER para ver métricas...")

def mostrar_metricas(nombres, tiempos):
    print("\n==================================")
    print("MÉTRICAS FINALES")
    print("==================================\n")

    tiempo_actual = 0
    total_espera = 0
    total_sistema = 0

    for i in range(len(nombres)):
        nombre = nombres[i]
        tiempo = tiempos[i]

        tiempo_espera = tiempo_actual
        tiempo_sistema = tiempo_espera + tiempo

        total_espera += tiempo_espera
        total_sistema += tiempo_sistema

        print(f"Persona/Proceso: {nombre}")
        print(f"  - Tiempo espera: {tiempo_espera}")
        print(f"  - Tiempo total:  {tiempo_sistema}\n")

        tiempo_actual += tiempo

    promedio_espera = total_espera / len(nombres)
    print(f"Promedio de espera: {round(promedio_espera, 2)}")
    print(f"Promedio en sistema: {round(total_sistema / len(nombres), 2)}")

def main():
    print("==================================")
    print("   SIMULADOR SO: FIFO + MEMORIA")
    print("==================================")
    
    nombres, tiempos, memorias = ingresar_personas()
    
    ejecutar_simulacion(nombres, tiempos, memorias)
    
    mostrar_metricas(nombres, tiempos)

if __name__ == "__main__":
    main()