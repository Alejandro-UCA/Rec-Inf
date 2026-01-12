import json
import re
import math
from busqueda.preProcesado import preprocesar_consulta

class Buscador:
    def __init__(self):
        self.indice = {}
        self.vectoresNormales = {}
        self.consulta = ""
        self.tipoIndice = ""
        self.logicaAplicada = ""
        self.top_n = 5    # Número de resultados a mostrar por defecto
    
    # pedirTipoIndice: Pregunta al usuario qué tipo de índice desea usar
    def pedirTipoIndice(self):
        print("¿Desea usar los indices Lematizados (1) o No Lematizados (2)?")
        self.tipoIndice = input("Ingrese 1 o 2: ")
        if self.tipoIndice not in ["1", "2"]:
            print("Opción inválida. Usando índice Lematizado por defecto.")
            self.tipoIndice = "1"

    # Permitir configurar cuántos documentos quiere ver el usuario en el ranking
    def pedirTopN(self):
        try:
            n = int(input("¿Cuántos documentos desea ver en el ranking?: "))
            if n > 0:
                self.top_n = n
        except:
            print("Valor no válido, usando N = 5 por defecto.")

    # Cargar índices
    def cargarIndices(self):
        if self.tipoIndice == "1":
            print("Cargando índices Lematizados...")
            try:
                with open("./resultados/indiceLematizado.json", "r", encoding="utf-8") as f:
                    self.indice = json.load(f)
                    if not self.indice:
                        raise ValueError("El archivo indiceLematizado.json está vacío")
                with open("./resultados/vectoresNormalesLematizado.json", "r", encoding="utf-8") as f:
                    self.vectoresNormales = json.load(f)
                    if not self.vectoresNormales:
                        raise ValueError("El archivo vectoresNormalesLematizado.json está vacío")
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                print(f"Error al cargar los índices: {e}")
        else:
            print("Cargando índices No Lematizados...")
            try:
                with open("./resultados/indiceNoLematizado.json", "r", encoding="utf-8") as f:
                    self.indice = json.load(f)
                    if not self.indice:
                        raise ValueError("El archivo indiceNoLematizado.json está vacío")
                with open("./resultados/vectoresNormalesNoLematizado.json", "r", encoding="utf-8") as f:
                    self.vectoresNormales = json.load(f)
                    if not self.vectoresNormales:
                        raise ValueError("El archivo vectoresNormalesNoLematizado.json está vacío")
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                print(f"Error al cargar los índices: {e}")

    # Obtener un fragmento del documento alrededor de la palabra o frase buscada
    def obtener_fragmento(self, documento, palabra):
        try:
            ruta = f"./corpus/{documento}"
            with open(ruta, "r", encoding="utf-8") as f:
                texto_original = f.read().split()
        except FileNotFoundError:
            return "(No se pudo abrir el documento)"

        # --- Normalizar tokens del documento ---
        texto_normalizado = []
        for t in texto_original:
            t_norm = re.sub(r'[^\w\s-]', '', t.lower())
            t_norm = re.sub(r'(?<!\w)-|-(?!\w)', '', t_norm)
            t_norm = re.sub(r'\b\w*\d+\b', '', t_norm)
            texto_normalizado.append(t_norm)

        # --- Normalizar la consulta (palabra o frase) ---
        palabra_norm = re.sub(r'[^\w\s-]', '', palabra.lower())
        palabra_norm = re.sub(r'(?<!\w)-|-(?!\w)', '', palabra_norm)
        tokens_consulta = palabra_norm.split()

        n = len(tokens_consulta)

        # --- Buscar palabra simple ---
        if n == 1:
            for i, t_norm in enumerate(texto_normalizado):
                if t_norm == tokens_consulta[0]:
                    inicio = max(0, i - 5)
                    fin = min(len(texto_original), i + 10)

                    fragmento_resaltado = []
                    for real, norm in zip(
                        texto_original[inicio:fin],
                        texto_normalizado[inicio:fin]
                    ):
                        if norm == tokens_consulta[0]:
                            fragmento_resaltado.append(f"**{real}**")
                        else:
                            fragmento_resaltado.append(real)

                    return " ".join(fragmento_resaltado)

        # --- Buscar frase exacta (ej. "way galaxy") ---
        else:
            for i in range(len(texto_normalizado) - n + 1):
                if texto_normalizado[i:i + n] == tokens_consulta:
                    inicio = max(0, i - 5)
                    fin = min(len(texto_original), i + n + 5)

                    fragmento_resaltado = []
                    for idx in range(inicio, fin):
                        real = texto_original[idx]
                        if i <= idx < i + n:
                            fragmento_resaltado.append(f"**{real}**")
                        else:
                            fragmento_resaltado.append(real)

                    return " ".join(fragmento_resaltado)

        return "(No se encontró un fragmento relevante)"

    # Calcular similitud coseno entre un documento y la consulta
    def calcular_similitud_coseno(self, documento, tokens_consulta):
        valor_absoluto_dj = self.vectoresNormales[documento]
        
        tokens_unicos = set(tokens_consulta)
        sumatorio = 0.0
        for palabra in tokens_unicos:
            if palabra in self.indice:
                sumatorio += (self.indice[palabra][0])**2
        valor_absoluto_q = math.sqrt(sumatorio)
        
        producto_escalar = 0.0
        for palabra in tokens_consulta: 
            if palabra in self.indice:
                tf_idf_dj = 0.0
                if documento in self.indice[palabra][1]:
                    tf_idf_dj = self.indice[palabra][1][documento][0]
                
                tf_idf_q = self.indice[palabra][0]
                producto_escalar += tf_idf_dj * tf_idf_q

        if valor_absoluto_dj == 0.0 or valor_absoluto_q == 0.0:
            return 0.0

        return producto_escalar / (valor_absoluto_dj * valor_absoluto_q)
    # Buscar la siguiente aparición de una frase en un texto tokenizado
    # parametros: frase_tokens: lista de terminos de la frase
    #             position: posición desde donde empezar a buscar
    def next_phrase(self, frase_tokens, doc, position=-1):
        n = len(frase_tokens)
        
        u = self.next_term(frase_tokens[0], doc, position)
        
        if u is None:
            return None
        
        v = u
        for i in range(1, n):
            v = self.next_term(frase_tokens[i], doc, v)
            if v is None:
                return self.next_phrase(frase_tokens, doc, position=u)

        if (v - u) == (n - 1):
            return (u, v)
        else:
            return self.next_phrase(frase_tokens, doc, position=u)

    def next_term(self, term, doc, position):
        if term not in self.indice:
            return None
        if doc not in self.indice[term][1]:
            return None

        posiciones = self.indice[term][1][doc][1]
        for pos in posiciones:
            if pos > position:
                return pos
        return None
    
    def procesar_Bloques(self, bloques_procesados):
        documentos_candidatos = None
        for bloque in bloques_procesados:
            documentos_bloque = set()
            for termino in bloque:
                if len(termino.split()) > 1:
                    # Frase exacta
                    tokens_frase = termino.split()
                    primera_palabra = tokens_frase[0]
                    if primera_palabra in self.indice:
                        documentos_tokens_frase = set(self.indice[primera_palabra][1].keys())
                        for documento in documentos_tokens_frase:
                            encontrado = False
                            pos = 0
                            while True:
                                resultado = self.next_phrase(tokens_frase, documento, pos)
                                if resultado is None:
                                    break
                                else:
                                    encontrado = True
                                    break
                            if encontrado:
                                documentos_bloque.add(documento)
                else:
                    #Token simple
                    if termino in self.indice:
                        documentos_termino = set(self.indice[termino][1].keys())
                        documentos_bloque.update(documentos_termino)
        if documentos_candidatos is None:
            documentos_candidatos = documentos_bloque
        else:
            documentos_candidatos.intersection_update(documentos_bloque)
        return documentos_candidatos

    # Pedir consulta al usuario y procesarla
    def pedirConsulta(self):
        consulta = input("Ingrese su consulta: ")
        print(f"Consulta recibida: {consulta}")
        
        if consulta.strip() == "":
            print("Consulta vacía. Por favor, ingrese una consulta válida.")
            return None
        
        # "way galaxy", WAY MILKY
        # 1) Separar la consulta por ANDs
        # 2) Tratar las comillas dobles como frases exactas
        # 3) Remplazar los ORs por " "
        # 4) Preprocesar la consulta según
        # Nos debería quedar: Bloques OR, cada bloque con términos (ANDs) y frases exactas (en otra variable)
        # 5) A los bloques normales de OR buscamos los documentos que contengan al menos un término de cada bloque
        # 6) A LAS FRASES le filtramos los documentos que no contengan las frases exactas y descartamos las que no valgan
        # 7) Hacemos la intersección de los documentos que cumplen cada bloque AND  
        
        self.consulta = consulta
        
        bloques_a_procesar, lista_de_tokens = preprocesar_consulta(consulta, self.tipoIndice)
        
        documentos_candidatos = self.procesar_Bloques(bloques_a_procesar)

        if not documentos_candidatos:
            return None
        
        lista_de_tokens = [palabra for token in lista_de_tokens for palabra in token.split()]

        documentos_con_similitud = []
        for doc in documentos_candidatos:
            similitud = self.calcular_similitud_coseno(doc, lista_de_tokens)
            documentos_con_similitud.append((doc, similitud))
        # Ordenar documentos por similitud (de mayor a menor)
        documentos_ordenados = sorted(documentos_con_similitud, key=lambda x: x[1], reverse=True)
        # Limitar a top N resultados
        documentos_ordenados = documentos_ordenados[:self.top_n]

        # Mostrar resultados
        print("\n===== RESULTADOS DEL RANKING =====")
        for doc, score in documentos_ordenados:
            print(f"\nDocumento: {doc}")
            print(f"Ranking: {score:.4f}")

            # Mostrar fragmento
            for termino in lista_de_tokens:
                fragmento = self.obtener_fragmento(doc, termino)
                print(f"Fragmento: {fragmento}")

        print("\n===== FIN RESULTADOS =====")

        return documentos_ordenados