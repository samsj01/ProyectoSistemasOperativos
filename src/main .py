import time
import threading

MEMORIA_RAM_TOTAL = 1000  # MB de capacidad del Servidor
memoria_en_uso = 0
archivo_log = "log_servidor.txt"
archivo_reporte = "reporte_rendimiento_web.txt"

# =====================================================================
# Cola Para ingresar a un servidor.
# =====================================================================
lock_memoria = threading.Lock()
lock_log = threading.Lock()

def guardar_log(mensaje):
    linea = f"[{time.strftime('%H:%M:%S')}] {mensaje}"
    # SECCIÓN CRÍTICA: Registro de eventos en el log del servidor
    with lock_log:
        with open(archivo_log, "a") as f:
            f.write(linea + "\n")
        print(linea)

def ingresar_personas():
    nombres = []
    tiempos = []
    memorias = []
    while True:
        print("\n--- PANEL DE CONFIGURACIÓN DE PETICIONES (REQUESTS) ---")
        nombre = input("ID de la Petición/Usuario: ")
        
        while True:
            try:
                tiempo = int(input("Carga de CPU requerida (Ciclos de procesamiento): "))
                if tiempo <= 0: raise ValueError
                break
            except ValueError:
                print("[Error] Ingrese un número entero positivo.")
                
        while True:
            try:
                memoria = int(input("Memoria de sesión requerida (MB): "))
                if memoria <= 0: raise ValueError
                break
            except ValueError:
                print("[Error] Ingrese un número entero positivo.")

        nombres.append(nombre)
        tiempos.append(tiempo)
        memorias.append(memoria)
        
        opcion = input("\n1. Añadir otra petición a la cola\n2. Iniciar Balanceador de Carga\nSeleccione: ")
        if opcion == "2":
            break
    return nombres, tiempos, memorias

def ejecutar_proceso(nombre, cpu_necesario, mem_necesaria, resultados, indice):
    global memoria_en_uso

    guardar_log(f"--- [REQ: {nombre}] Entrando al pipeline (Worker Thread: {threading.current_thread().name}) ---")

    # SECCIÓN CRÍTICA: Asignación de recursos en el pool del servidor
    with lock_memoria:
        if (memoria_en_uso + mem_necesaria) <= MEMORIA_RAM_TOTAL:
            memoria_en_uso += mem_necesaria
            modo = "MEMORIA RAM"
            velocidad = 0.1  # Latencia baja
            guardar_log(f"[OK] {nombre} -> Alojado en RAM ({mem_necesaria}MB). Carga actual: {memoria_en_uso}/{MEMORIA_RAM_TOTAL}MB")
        else:
            modo = "SWAP (DISCO)"
            velocidad = 0.4  # Latencia alta por saturación
            guardar_log(f"[OVERLOAD] {nombre} -> RAM Insuficiente. Derivado a Memoria Virtual (Lento)")

    # Simulación de procesamiento de la solicitud
    tiempo_inicio = time.time()
    for ciclo in range(1, cpu_necesario + 1):
        time.sleep(velocidad)
        with lock_log:
            print(f" > [SERVER] Procesando Request '{nombre}': Ciclo {ciclo}/{cpu_necesario} en {modo}...")

    tiempo_total = round(time.time() - tiempo_inicio, 2)

    # SECCIÓN CRÍTICA: Liberación de recursos del servidor
    if modo == "MEMORIA RAM":
        with lock_memoria:
            memoria_en_uso -= mem_necesaria
            guardar_log(f"[FIN] {nombre} procesado en {tiempo_total}s | Sesión cerrada. RAM Disponible: {MEMORIA_RAM_TOTAL - memoria_en_uso}MB")
    else:
        guardar_log(f"[FIN] {nombre} procesado en {tiempo_total}s | Finalizado desde SWAP.")

    resultados[indice] = tiempo_total


def ejecutar_simulacion(nombres, tiempos, memorias, algoritmo_nombre):
    global memoria_en_uso
    memoria_en_uso = 0

    guardar_log(f"\n=== INICIANDO DESPACHO DE PETICIONES - ESTRATEGIA: {algoritmo_nombre} ===")
    
    resultados = [None] * len(nombres)
    hilos = []

    for i in range(len(nombres)):
        hilo = threading.Thread(
            target=ejecutar_proceso,
            args=(nombres[i], tiempos[i], memorias[i], resultados, i),
            name=f"Worker-{nombres[i]}"
        )
        hilos.append(hilo)

    for hilo in hilos:
        hilo.start()

    for hilo in hilos:
        hilo.join()

    guardar_log(f"=== TODAS LAS PETICIONES COMPLETADAS BAJO {algoritmo_nombre} ===")
    return resultados


def calcular_metricas(nombres, tiempos, tiempos_reales):
    total_espera = 0
    total_sistema = 0
    tiempo_acumulado_espera = 0
    detalles = []

    for i in range(len(nombres)):
        real = tiempos_reales[i] if tiempos_reales[i] is not None else 0
        tiempo_espera = tiempo_acumulado_espera
        tiempo_sistema = tiempo_espera + real
        
        total_espera += tiempo_espera
        total_sistema += tiempo_sistema
        
        detalles.append({
            "nombre": nombres[i],
            "turnos": tiempos[i],
            "real": real,
            "espera": tiempo_espera,
            "sistema": tiempo_sistema
        })
        tiempo_acumulado_espera += real

    prom_espera = round(total_espera / len(nombres), 2)
    prom_sistema = round(total_sistema / len(nombres), 2)
    
    return prom_espera, prom_sistema, detalles


def guardar_reporte_archivo(reporte_texto):
    with open(archivo_reporte, "w") as f:
        f.write(reporte_texto)
    print(f"\n[OK] Informe técnico generado en '{archivo_reporte}'")


def main():
    print("==================================================")
    print("      SERVER LOAD SIMULATOR - HTTP REQUESTS")
    print("      Gestión de Hilos, RAM/SWAP y Latencia")
    print("==================================================")

    nombres, tiempos, memorias = ingresar_personas()
    datos_originales = list(zip(nombres, tiempos, memorias))

    # --- SIMULACIÓN 1: FIFO ---
    input("\n[ENTER] Iniciar Simulación 1: Despacho Secuencial (FIFO)...")
    open(archivo_log, "w").close() 
    
    nombres_fifo = [d[0] for d in datos_originales]
    tiempos_fifo = [d[1] for d in datos_originales]
    memorias_fifo = [d[2] for d in datos_originales]
    
    reales_fifo = ejecutar_simulacion(nombres_fifo, tiempos_fifo, memorias_fifo, "FIFO")
    p_espera_fifo, p_sistema_fifo, det_fifo = calcular_metricas(nombres_fifo, tiempos_fifo, reales_fifo)

    # --- SIMULACIÓN 2: SJF ---
    input("\n[ENTER] Iniciar Simulación 2: Optimización de Carga Corta (SJF)...")
    datos_sjf = sorted(datos_originales, key=lambda x: x[1])
    
    nombres_sjf = [d[0] for d in datos_sjf]
    tiempos_sjf = [d[1] for d in datos_sjf]
    memorias_sjf = [d[2] for d in datos_sjf]
    
    reales_sjf = ejecutar_simulacion(nombres_sjf, tiempos_sjf, memorias_sjf, "SJF")
    p_espera_sjf, p_sistema_sjf, det_sjf = calcular_metricas(nombres_sjf, tiempos_sjf, reales_sjf)

    # --- GENERACIÓN DE REPORTE ---
    output = []
    output.append("\n==================================================")
    output.append("        INFORME DE RENDIMIENTO DEL SERVIDOR")
    output.append("==================================================")
    
    output.append("\n>>> MÉTRICAS ESTRATEGIA FIFO:")
    for d in det_fifo:
        output.append(f" Request {d['nombre']} -> CPU: {d['turnos']} ciclos | T. Real: {d['real']}s | Espera en Cola: {d['espera']}s | T. Respuesta: {d['sistema']}s")
    output.append(f" * Latencia Promedio Espera FIFO: {p_espera_fifo}s")
    output.append(f" * Tiempo Promedio de Respuesta FIFO: {p_sistema_fifo}s")

    output.append("\n>>> MÉTRICAS ESTRATEGIA SJF (Priority):")
    for d in det_sjf:
        output.append(f" Request {d['nombre']} -> CPU: {d['turnos']} ciclos | T. Real: {d['real']}s | Espera en Cola: {d['espera']}s | T. Respuesta: {d['sistema']}s")
    output.append(f" * Latencia Promedio Espera SJF: {p_espera_sjf}s")
    output.append(f" * Tiempo Promedio de Respuesta SJF: {p_sistema_sjf}s")
    
    output.append("\n==================================================")
    output.append("                ANÁLISIS DE CARGA")
    output.append("==================================================")
    if p_espera_sjf < p_espera_fifo:
        output.append(" Análisis: La optimización SJF mejoró la experiencia del usuario al reducir la cola de espera.")
    else:
        output.append(" Análisis: Ambas estrategias respondieron igual bajo esta carga específica.")
    output.append(f" Capacidad RAM del servidor controlada a: {MEMORIA_RAM_TOTAL}MB")
    output.append(" Seguridad: Los Locks de exclusión mutua protegieron la integridad del servidor ante accesos concurrentes.")

    texto_final = "\n".join(output)
    print(texto_final)
    guardar_reporte_archivo(texto_final)

if __name__ == "__main__":
    main()