from . import crawler
from . import preProcesado
import os
import json
import concurrent.futures # Librería para paralelismo

# Función auxiliar que procesa UN solo archivo
# Debe estar fuera de indexacion() para que funcione el paralelismo
def preProcesarTrabajoHilo(ruta_completa):
    try:
        # Extraemos el nombre del archivo de la ruta
        nombre_archivo = os.path.basename(ruta_completa)
        
        with open(ruta_completa, "r", encoding="utf-8") as f:
            texto = f.read()
            
        # Procesamos
        sin_lem, con_lem = preProcesado.preprocesar_texto(texto)
        
        # Retornamos el resultado para este archivo
        return nombre_archivo, {"sin_lematizar": sin_lem, "lematizado": con_lem}
    except Exception as e:
        print(f"Error en {ruta_completa}: {e}")
        return None

def indexacion():
    crawler.crawler()
    ruta_corpus = "./corpus/"
    
    # Usamos os.scandir en lugar de listdir (es más rápido leyendo directorios)
    # Creamos una lista con las rutas COMPLETAS
    rutas_archivos = [entry.path for entry in os.scandir(ruta_corpus) if entry.is_file()]
    
    textoPreProcesado = {}

    print(f"Procesando {len(rutas_archivos)} archivos en paralelo...")

    # ProcessPoolExecutor usa múltiples núcleos de la CPU
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # map aplica la función a cada archivo de la lista
        resultados = executor.map(preProcesarTrabajoHilo, rutas_archivos)

        # Recogemos los resultados a medida que terminan
        for resultado in resultados:
            if resultado:
                nombre, datos = resultado
                textoPreProcesado[nombre] = datos

    # Guardado final
    with open("./resultados/textoPreProcesado.json", "w", encoding="utf-8") as f:
        json.dump(textoPreProcesado, f, ensure_ascii=False, indent=4)