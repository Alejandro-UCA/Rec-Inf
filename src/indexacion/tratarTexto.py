import json
import math

def tf_idf(indiceLem, indiceNoLem, corpus):
    palabras_documento = {} #Número total de palabras por documento
    vectores_normales_documento_lem = {} #Para guardar la norma de cada vector de cada documento (lematizado)
    vectores_normales_documento_no_lem = {} #Para guardar la norma de cada vector de cada documento (no lematizado)

    if not corpus:
        with open("./resultados/textoPreProcesado.json", "r", encoding="utf-8") as f:
            corpus = json.load(f)
    
    for doc_nombre, contenido in corpus.items():
        #UN DOCUMENTO
        texto_lem = contenido["lematizado"]
        texto_no_lem = contenido["sin_lematizar"]
        
        palabras_lem = texto_lem.split()
        palabras_no_lem = texto_no_lem.split()
        
        #Caso del texto lematizado
        for i, palabra in enumerate(palabras_lem, 1): #Ese 1 es para que i empiece en 1 y no en 0
            #Vamos a llevar un conteo de las palabras que aparecen en este documento
            #Guardaremos cúantas veces sale cada palabra y en las posiciones que aparece
            if palabra not in palabras_documento:
                palabras_documento[palabra] = {"total": 1, "posiciones": [i]}
            else:
                palabras_documento[palabra]["total"] += 1
                palabras_documento[palabra]["posiciones"].append(i)
        
        #Una vez hayamos contado todas las veces que aparecen las palabras en el documento
        #vamos a actualizar el índice
        for palabra, datos in palabras_documento.items():
            tf_palabra_en_documento = 1 + math.log2(datos["total"])
            #vamos a ver si la palabra está o no en el índice
            if palabra not in indiceLem:
                #Si la palabra no está, la añadimos
                indiceLem[palabra] = [1, {}]
                indiceLem[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
            else:
                #Si ya está en el índice, solo tenemos que añadir los datos de este documento
                indiceLem[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
                indiceLem[palabra][0] += 1 #Aumentamos en 1 el número de documentos donde aparece
        
        palabras_documento = {} #Reseteamos ya que ahora contaremos las del texto sin lematizar
        #Caso del texto sin lematizar
        for i, palabra in enumerate(palabras_no_lem, 1): #Ese 1 es para que i empiece en 1 y no en 0
            #Vamos a llevar un conteo de las palabras que aparecen en este documento
            #Guardaremos cúantas veces sale cada palabra y en las posiciones que aparece
            if palabra not in palabras_documento:
                palabras_documento[palabra] = {"total": 1, "posiciones": [i]}
            else:
                palabras_documento[palabra]["total"] += 1
                palabras_documento[palabra]["posiciones"].append(i)
        
        #Una vez hayamos contado todas las veces que aparecen las palabras en el documento
        #vamos a actualizar el índice
        for palabra, datos in palabras_documento.items():
            tf_palabra_en_documento = 1 + math.log2(datos["total"])
            #vamos a ver si la palabra está o no en el índice
            if palabra not in indiceNoLem:
                #Si la palabra no está, la añadimos
                indiceNoLem[palabra] = [1, {}]
                indiceNoLem[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
            else:
                #Si ya está en el índice, solo tenemos que añadir los datos de este documento
                indiceNoLem[palabra][1][doc_nombre] = [tf_palabra_en_documento, datos["posiciones"]]
                indiceNoLem[palabra][0] += 1 #Aumentamos en 1 el número de documentos donde aparece
        
        palabras_documento = {} #Reseteamos para el siguiente documento

    #Aquí, ya hemos procesado todos los documentos por lo que tenemos "ni" en las posiciones indiceLem[palabra][0]
    #y los tfs en indiceLem[palabra][1][doc_nombre][0]
    #Ahora calcularemos los IDFs de cada palabra y calcularemos los TF-IDF de cada palabra en cada documento
    nCorpus = len(corpus) #Número total de documentos en el corpus

    #Calculamos los IDF y TF-IDF para el texto lematizado
    for palabra, datos in indiceLem.items():
        ni = datos[0]
        idf = math.log2(nCorpus / ni)
        #Ahora actualizamos el IDF en el índice
        indiceLem[palabra][0] = idf
        #Ahora calculamos el TF-IDF para cada documento donde aparece la palabra
        for doc_nombre, tf_y_posiciones in datos[1].items():
            tf = tf_y_posiciones[0]
            tf_idf_valor = tf * idf
            #Actualizamos el valor en el índice
            indiceLem[palabra][1][doc_nombre][0] = tf_idf_valor
            vectores_normales_documento_lem[doc_nombre] = vectores_normales_documento_lem.get(doc_nombre, 0) + tf_idf_valor**2
    
    #Calculamos los IDF y TF-IDF para el texto sin lematizar
    for palabra, datos in indiceNoLem.items():
        ni = datos[0]
        idf = math.log2(nCorpus / ni)
        #Ahora actualizamos el IDF en el índice
        indiceNoLem[palabra][0] = idf
        #Ahora calculamos el TF-IDF para cada documento donde aparece la palabra
        for doc_nombre, tf_y_posiciones in datos[1].items():
            tf = tf_y_posiciones[0]
            tf_idf_valor = tf * idf
            #Actualizamos el valor en el índice
            indiceNoLem[palabra][1][doc_nombre][0] = tf_idf_valor
            vectores_normales_documento_no_lem[doc_nombre] = vectores_normales_documento_no_lem.get(doc_nombre, 0) + tf_idf_valor**2
    
    #Finalmente, calculamos la norma de cada vector
    for doc_nombre in vectores_normales_documento_lem:
        vectores_normales_documento_lem[doc_nombre] = math.sqrt(vectores_normales_documento_lem[doc_nombre])
    
    for doc_nombre in vectores_normales_documento_no_lem:
        vectores_normales_documento_no_lem[doc_nombre] = math.sqrt(vectores_normales_documento_no_lem[doc_nombre])
    
    #Ya hemos calculado todo despues de tanto jaleo, ahora ya podemos devolverlos
    return indiceLem, indiceNoLem, vectores_normales_documento_lem, vectores_normales_documento_no_lem