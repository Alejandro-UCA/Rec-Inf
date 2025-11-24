import re
import spacy
from . import crawler
import os
import json
import concurrent.futures # Librería para paralelismo

#spaCy es una lobrería para procesamiento del lenguaje natural (NLP) en Python
#Ya que en el proyecto se nos pide utilizar NLP, usaremos spaCy para la lematización

nlp = spacy.load("en_core_web_sm") #Este es el modelo en inglés

def preprocesar_texto(texto):
    """
    Función para preprocesar el texto. Esta función también devuelve dos versiones del texto:
    - Una sin lematizar
    - Otra lematizada
    Los pasos que se siguen son:
    1. Convertir a minúsculas
    2. Eliminar caracteres especiales
    3. Eliminar guiones que no estén entre palabras
    4. Limpiar espacios extra
    5. Lematización y no lematización
    6. Devolver ambas versiones del texto
    Args:
        texto (str): El texto a preprocesar.
    Returns:
        tuple: Una tupla con dos elementos:
            - textoSinLematizar (str): El texto preprocesado sin lematización.
            - textoLematizado (str): El texto preprocesado con lematización.
    """
    # Primer tratamiento, convertimos todo el texto a minúsculas
    texto = texto.lower()

    # Segundo tratamiento: Eliminamos los caracteres especiales
    texto = re.sub(r'[^\w\s-]', '', texto)

    # Tercer tratamiento: Eliminamos guiones que no estén entre palabras
    texto = re.sub(r'(?<!\w)-|-(?!\w)', '', texto)

    # Cuarto tratamiento: Limpiar espacios extra que hayan podido quedar por ahi sueltos
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Quinto tratamiento: Una palabra no puede terminar en numeros
    texto = re.sub(r'\b\w*\d+\b', '', texto)

    # Sexto tratamiento: Lematización? Dos versiones aqui, una con Spacy y otra sin Spacy
    textoSinLematizar = texto
    textoLematizado = lematizar_texto(texto)

    # Sexto tratamiento específico para el texto lematizado: spaCy destroza las palabras con guiones y hay que arreglarlas
    textoLematizado = re.sub(r'\s+-\s+', '-', textoLematizado)

    return textoSinLematizar, textoLematizado

def lematizar_texto(texto):
    """
    Función para lematizar el texto usando spaCy.
    Args:
        texto (str): El texto a lematizar.
    Returns:
        str: El texto lematizado.
    """
    
    # Convertimos el texto limpio a un objeto Doc de spaCy
    doc = nlp(texto)
    
    # Extraemos los "lemas" o formas base de cada token (infinitivos por ejemplo en verbos)
    # spaCy es inteligente: si ve "running", el lema es "run".
    # Si ve "better", el lema es "good".
    lemas = [token.lemma_ for token in doc]
    
    # Unimos de nuevo en un string
    return " ".join(lemas)

# Función auxiliar que procesa UN solo archivo
# Debe estar fuera de indexacion() para que funcione el paralelismo
def preProcesarTrabajoHilo(ruta_completa):
    try:
        # Extraemos el nombre del archivo de la ruta
        nombre_archivo = os.path.basename(ruta_completa)
        
        with open(ruta_completa, "r", encoding="utf-8") as f:
            texto = f.read()
            
        # Procesamos
        sin_lem, con_lem = preprocesar_texto(texto)
        
        # Retornamos el resultado para este archivo
        return nombre_archivo, {"sin_lematizar": sin_lem, "lematizado": con_lem}
    except Exception as e:
        print(f"Error en {ruta_completa}: {e}")
        return None

def preProcesamiento():
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

    return textoPreProcesado