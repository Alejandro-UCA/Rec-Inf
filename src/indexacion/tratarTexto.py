import json
import math

def procesar_documento(palabras, indice, doc_nombre, palabras_documento):
    for i, palabra in enumerate(palabras, 1): # Ese 1 es para que i empiece en 1 y no en 0
        # Vamos a llevar un conteo de las palabras que aparecen en este documento
        # Guardaremos cúantas veces sale cada palabra y en las posiciones que aparece
        if palabra not in palabras_documento:
            palabras_documento[palabra] = {"total": 1, "posiciones": [i]}
        else:
            palabras_documento[palabra]["total"] += 1
            palabras_documento[palabra]["posiciones"].append(i)
    
    # Una vez hayamos contado todas las veces que aparecen las palabras en el documento
    # vamos a actualizar el índice
    for palabra, datos in palabras_documento.items():
        tf_palabra_en_documento = 1 + math.log2(datos["total"])
        # vamos a ver si la palabra está o no en el índice
        if palabra not in indice:
            # Si la palabra no está, la añadimos
            indice[palabra] = [1, {}]
            indice[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
        else:
            # Si ya está en el índice, solo tenemos que añadir los datos de este documento
            indice[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
            indice[palabra][0] += 1 # Aumentamos en 1 el número de documentos donde aparece
        
def calcularTF_IDF(indice, nCorpus, vectores_normales_documento):
    for palabra, datos in indice.items():
        ni = datos[0]
        idf = math.log2(nCorpus / ni)
        # Ahora actualizamos el IDF en el índice
        indice[palabra][0] = idf
        # Ahora calculamos el TF-IDF para cada documento donde aparece la palabra
        for doc_nombre, tf_y_posiciones in datos[1].items():
            tf = tf_y_posiciones[0]
            tf_idf_valor = tf * idf
            # Actualizamos el valor en el índice
            indice[palabra][1][doc_nombre][0] = tf_idf_valor
            vectores_normales_documento[doc_nombre] = vectores_normales_documento.get(doc_nombre, 0) + tf_idf_valor**2

def calcularFormaNormal(vectores_normales_documento):
    for doc_nombre in vectores_normales_documento:
        vectores_normales_documento[doc_nombre] = math.sqrt(vectores_normales_documento[doc_nombre])

def tf_idf(corpus):
    indiceLem = {} # Índice para el texto lematizado
    indiceNoLem = {} # Índice para el texto sin lematizar
    palabras_documento = {} # Número total de palabras por documento
    vectores_normales_documento_lem = {} # Para guardar la norma de cada vector de cada documento (lematizado)
    vectores_normales_documento_no_lem = {} # Para guardar la norma de cada vector de cada documento (no lematizado)

    if not corpus:
        with open("./resultados/textoPreProcesado.json", "r", encoding="utf-8") as f:
            corpus = json.load(f)
    
    for doc_nombre, contenido in corpus.items():
        # Dentro del for tratamos cada documento individualmente
        texto_lem = contenido["lematizado"]
        texto_no_lem = contenido["sin_lematizar"]
        
        palabras_lem = texto_lem.split()
        palabras_no_lem = texto_no_lem.split()
        
        # Caso del texto lematizado
        palabras_documento = {} # Reseteamos ya que ahora contaremos las del texto sin lematizar
        procesar_documento(palabras_lem, indiceLem, doc_nombre, palabras_documento)
        # Caso del texto sin lematizar
        palabras_documento = {} # Reseteamos para el siguiente documento
        procesar_documento(palabras_no_lem, indiceNoLem, doc_nombre, palabras_documento)

    # Aquí, ya hemos procesado todos los documentos por lo que tenemos "ni" en las posiciones indiceLem[palabra][0]
    # y los tfs en indiceLem[palabra][1][doc_nombre][0]
    # Ahora calcularemos los IDFs de cada palabra y calcularemos los TF-IDF de cada palabra en cada documento
    nCorpus = len(corpus) # Número total de documentos en el corpus

    # Calculamos los IDF y TF-IDF para el texto lematizado
    calcularTF_IDF(indiceLem, nCorpus, vectores_normales_documento_lem)

    # Calculamos los IDF y TF-IDF para el texto sin lematizar
    calcularTF_IDF(indiceNoLem, nCorpus, vectores_normales_documento_no_lem)
    
    # Finalmente, calculamos la norma de cada vector
    calcularFormaNormal(vectores_normales_documento_lem)
    calcularFormaNormal(vectores_normales_documento_no_lem)
    # Ya hemos calculado todo despues de tanto jaleo, ahora ya podemos devolverlos
    return indiceLem, indiceNoLem, vectores_normales_documento_lem, vectores_normales_documento_no_lem