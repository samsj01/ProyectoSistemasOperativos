import time
import threading

MEMORIA_RAM_TOTAL = 1000  # MB
memoria_en_uso = 0
archivo_log = "log_entrega_2.txt"

# =============================================
# PUNTO 1 Y 2: Lock para sincronización real
# Protege la variable compartida memoria_en_uso
# =============================================
lock_memoria = threading.Lock()
lock_log = threading.Lock()

def guardar_log(mensaje):
    linea = f"[{time.strftime('%H:%M:%S')}] {mensaje}"
    # PUNTO 2: Sincronización - solo un hilo escribe al log a la vez
    with lock_log:
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

# =============================================
# PUNTO 1: Cada proceso corre en su propio hilo
# PUNTO 2: Lock protege memoria_en_uso compartida
# =============================================
def ejecutar_proceso(nombre, cpu_necesario, mem_necesaria, resultados, indice):
    global memoria_en_uso

    guardar_log(f"--- [{nombre}] iniciando (hilo {threading.current_thread().name}) ---")

    # PUNTO 2: Sección crítica - revisar y modificar memoria compartida
    with lock_memoria:
        if (memoria_en_uso + mem_necesaria) <= MEMORIA_RAM_TOTAL:
            memoria_en_uso += mem_necesaria
            modo = "RAM"
            velocidad = 0.1
            guardar_log(f"[{nombre}] → RAM asignada ({mem_necesaria}MB). Uso total: {memoria_en_uso}/{MEMORIA_RAM_TOTAL}MB")
        else:
            modo = "SWAP (Disco)"
            velocidad = 0.5
            guardar_log(f"[{nombre}] → Sin RAM disponible, usando SWAP (lento)")

    # Ejecución de ciclos (fuera del lock para permitir concurrencia real)
    tiempo_inicio = time.time()
    for ciclo in range(1, cpu_necesario + 1):
        time.sleep(velocidad)
        with lock_log:
            print(f" > [{nombre}] Ejecutando ciclo {ciclo}/{cpu_necesario} en {modo}...")

    tiempo_total = round(time.time() - tiempo_inicio, 2)

    # PUNTO 2: Sección crítica - liberar memoria compartida
    if modo == "RAM":
        with lock_memoria:
            memoria_en_uso -= mem_necesaria
            guardar_log(f"[{nombre}] ✓ Finalizado en {tiempo_total}s | RAM liberada. Disponible: {MEMORIA_RAM_TOTAL - memoria_en_uso}MB")
    else:
        guardar_log(f"[{nombre}] ✓ Finalizado en {tiempo_total}s | Terminó en SWAP.")

    # Guardar resultado para métricas
    resultados[indice] = tiempo_total


def ejecutar_simulacion(nombres, tiempos, memorias):
    global memoria_en_uso
    memoria_en_uso = 0

    open(archivo_log, "w").close()
    guardar_log("=== INICIANDO EJECUCIÓN CON CONCURRENCIA REAL ===")
    guardar_log(f"=== Procesos a ejecutar: {len(nombres)} | Hilos simultáneos ===")

    print("\n==================================")
    print("EJECUCIÓN CONCURRENTE EN TIEMPO REAL")
    print("==================================\n")

    resultados = [None] * len(nombres)
    hilos = []

    # PUNTO 1: Crear un hilo por proceso (concurrencia real)
    for i in range(len(nombres)):
        hilo = threading.Thread(
            target=ejecutar_proceso,
            args=(nombres[i], tiempos[i], memorias[i], resultados, i),
            name=f"Hilo-{nombres[i]}"
        )
        hilos.append(hilo)

    # PUNTO 1: Lanzar todos los hilos al mismo tiempo
    guardar_log(f"Lanzando {len(hilos)} hilos concurrentemente...")
    for hilo in hilos:
        hilo.start()

    # Esperar a que todos terminen
    for hilo in hilos:
        hilo.join()

    guardar_log("=== TODOS LOS PROCESOS TERMINARON ===")
    input("\nEjecución terminada. Presione ENTER para ver métricas...")
    return resultados


def mostrar_metricas(nombres, tiempos, tiempos_reales):
    print("\n==================================")
    print("MÉTRICAS FINALES")
    print("==================================\n")

    tiempo_actual = 0
    total_espera = 0
    total_sistema = 0

    for i in range(len(nombres)):
        nombre = nombres[i]
        tiempo = tiempos[i]
        real = tiempos_reales[i] if tiempos_reales[i] is not None else 0

        tiempo_espera = tiempo_actual
        tiempo_sistema = tiempo_espera + tiempo
        total_espera += tiempo_espera
        total_sistema += tiempo_sistema

        print(f"Proceso: {nombre}")
        print(f"  - Ciclos estimados:    {tiempo}")
        print(f"  - Tiempo real (s):     {real}")
        print(f"  - Tiempo espera FIFO:  {tiempo_espera}")
        print(f"  - Tiempo total FIFO:   {tiempo_sistema}\n")

        tiempo_actual += tiempo

    promedio_espera = total_espera / len(nombres)
    print(f"Promedio de espera:    {round(promedio_espera, 2)}")
    print(f"Promedio en sistema:   {round(total_sistema / len(nombres), 2)}")
    print(f"\nNota: Los procesos corrieron en paralelo (hilos reales).")
    print(f"      La sincronización con Lock evitó condiciones de carrera en la RAM.")


def main():
    print("==================================")
    print("  SIMULADOR SO: FIFO + MEMORIA")
    print("  + Concurrencia y Sincronización")
    print("==================================")

    nombres, tiempos, memorias = ingresar_personas()
    tiempos_reales = ejecutar_simulacion(nombres, tiempos, memorias)
    mostrar_metricas(nombres, tiempos, tiempos_reales)

if __name__ == "__main__":
    main()
