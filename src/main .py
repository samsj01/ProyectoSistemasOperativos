import time
import multiprocessing

# ==================== CONFIGURACIÓN ====================
MEMORIA_RAM_TOTAL = 1000  # MB
archivo_log = "log_entrega_2.txt"

# Recursos compartidos entre procesos
lock_recursos = multiprocessing.Lock()
memoria_en_uso = multiprocessing.Value('i', 0)  # Variable compartida segura

def guardar_log(mensaje):
    linea = f"[{time.strftime('%H:%M:%S')}] {mensaje}"
    print(linea)
    with lock_recursos:
        with open(archivo_log, "a") as f:
            f.write(linea + "\n")

def procesar_persona(nombre, cpu_necesario, mem_necesaria):
    """Función que ejecuta cada proceso de forma independiente (concurrencia real)"""
    
    guardar_log(f"--- Siguiente: {nombre} (Pide {mem_necesaria}MB) ---")
    
    # Solicitud de memoria (protegida)
    with lock_recursos:
        if (memoria_en_uso.value + mem_necesaria) <= MEMORIA_RAM_TOTAL:
            memoria_en_uso.value += mem_necesaria
            modo = "RAM"
            velocidad = 0.1
            guardar_log(f"ESTADO: {nombre} Esta siendo Atendido. Uso actual: {memoria_en_uso.value}/{MEMORIA_RAM_TOTAL}MB")
        else:
            modo = "SWAP (Disco)"
            velocidad = 0.5
            guardar_log(f"ESTADO: {nombre} usa SWAP por falta de espacio")

    # Simulación de ejecución de ciclos de CPU
    for ciclo in range(1, cpu_necesario + 1):
        time.sleep(velocidad)
        print(f" > {nombre}: Ejecutando {ciclo}/{cpu_necesario} en {modo}...")

    # Liberación de memoria (protegida)
    with lock_recursos:
        if modo == "RAM":
            memoria_en_uso.value -= mem_necesaria
            guardar_log(f"FINALIZADO: {nombre} liberó RAM. RAM Disponible: {MEMORIA_RAM_TOTAL - memoria_en_uso.value}MB")
        else:
            guardar_log(f"FINALIZADO: {nombre} terminó ejecución en SWAP.")


def ejecutar_simulacion(nombres, tiempos, memorias):
    # Limpieza del archivo de log
    with lock_recursos:
        open(archivo_log, "w").close()
    
    guardar_log("=== INICIANDO EJECUCIÓN CON GESTIÓN DE MEMORIA Y CONCURRENCIA REAL (MULTICORE) ===")
    
    print("\n==================================")
    print("EJECUCIÓN EN TIEMPO REAL - CONCURRENCIA REAL")
    print("==================================\n")

    procesos = []

    # === AQUÍ ESTÁ LA CONCURRENCIA REAL ===
    # Lanzamos todos los procesos al mismo tiempo
    for i in range(len(nombres)):
        p = multiprocessing.Process(
            target=procesar_persona,
            args=(nombres[i], tiempos[i], memorias[i])
        )
        procesos.append(p)
        p.start()

    # Esperamos que todos terminen
    for p in procesos:
        p.join()

    guardar_log("=== EJECUCIÓN FINALIZADA CON CONCURRENCIA REAL ===")
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
        print(f" - Tiempo espera: {tiempo_espera}")
        print(f" - Tiempo total: {tiempo_sistema}\n")
        tiempo_actual += tiempo
    
    if len(nombres) > 0:
        print(f"Promedio de espera: {round(total_espera / len(nombres), 2)}")
        print(f"Promedio en sistema: {round(total_sistema / len(nombres), 2)}")


def main():
    print("==================================")
    print(" SIMULADOR SO: FIFO + MEMORIA + CONCURRENCIA REAL")
    print("==================================\n")
    
    nombres, tiempos, memorias = ingresar_personas()
    
    if nombres:
        ejecutar_simulacion(nombres, tiempos, memorias)
        mostrar_metricas(nombres, tiempos)
    else:
        print("No se ingresaron procesos.")


# ==================== FUNCIÓN DE INGRESO (sin cambios) ====================
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


if __name__ == "__main__":
    main()
