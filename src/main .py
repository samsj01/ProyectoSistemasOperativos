import time
import random
import threading  
#SINCRONIZACIÓN 
# Creamos un Lock (Cerrojo) para proteger los recursos compartidos:
# 1. El archivo de LOG (Escritura en disco)
# 2. La variable memoria_en_uso (Recurso crítico de RAM)
# =================================================================
lock_recursos = threading.Lock() 

MEMORIA_RAM_TOTAL = 1000  # MB
memoria_en_uso = 0
archivo_log = "log_entrega_2.txt"

def guardar_log(mensaje):
    linea = f"[{time.strftime('%H:%M:%S')}] {mensaje}"
    
    # SINCRONIZACIÓN: Bloqueamos el archivo para que nadie más escriba
    with lock_recursos:
        with open(archivo_log, "a") as f:
            f.write(linea + "\n")
    # El archivo se libera automáticamente aquí
    
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
    
    # Limpieza inicial del log protegida
    with lock_recursos:
        open(archivo_log, "w").close()
        
    guardar_log("=== INICIANDO EJECUCIÓN CON GESTIÓN DE MEMORIA (SINCRONIZADA) ===")
    
    print("\n==================================")
    print("EJECUCIÓN EN TIEMPO REAL")
    print("==================================\n")

    for i in range(len(nombres)):
        nombre = nombres[i]
        cpu_necesario = tiempos[i]
        mem_necesaria = memorias[i]

        guardar_log(f"--- Siguiente: {nombre} (Pide {mem_necesaria}MB) ---")

        # SINCRONIZACIÓN: Protegemos el acceso a la RAM
        # Esto evita "Condiciones de Carrera" (Race Conditions)
        with lock_recursos:
            if (memoria_en_uso + mem_necesaria) <= MEMORIA_RAM_TOTAL:
                memoria_en_uso += mem_necesaria
                modo = "RAM"
                velocidad = 0.1
                guardar_log(f"ESTADO: {nombre} atendido. Uso RAM: {memoria_en_uso}/{MEMORIA_RAM_TOTAL}MB")
            else:
                modo = "SWAP (Disco)"
                velocidad = 0.5 
                guardar_log(f"ESTADO: {nombre} usa SWAP por falta de espacio")
        # La variable de memoria queda libre para otros procesos

        for ciclo in range(1, cpu_necesario + 1):
            time.sleep(velocidad) 
            print(f" > {nombre}: Ejecutando {ciclo}/{cpu_necesario} en {modo}...")

        # SINCRONIZACIÓN: Protegemos la liberación de RAM
        if modo == "RAM":
            with lock_recursos:
                memoria_en_uso -= mem_necesaria
            guardar_log(f"FINALIZADO: {nombre} liberó RAM. Disponible: {MEMORIA_RAM_TOTAL - memoria_en_uso}MB")
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

    if len(nombres) > 0:
        print(f"Promedio de espera: {round(total_espera / len(nombres), 2)}")
        print(f"Promedio en sistema: {round(total_sistema / len(nombres), 2)}")

def main():
    print("==================================")
    print("   SIMULADOR SO: FIFO + MEMORIA")
    print("==================================")
    
    nombres, tiempos, memorias = ingresar_personas()
    
    if nombres:
        ejecutar_simulacion(nombres, tiempos, memorias)
        mostrar_metricas(nombres, tiempos)
    else:
        print("No se ingresaron procesos.")

if __name__ == "__main__":
    main()
