import json
import re
import math
from indexacion.preProcesado import preprocesar_texto

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

    # Obtener un fragmento del documento alrededor de la palabra buscada
    def obtener_fragmento(self, documento, palabra):
        try:
            ruta = f"./corpus/{documento}"
            with open(ruta, "r", encoding="utf-8") as f:
                texto_original = f.read().split()
        except FileNotFoundError:
            return "(No se pudo abrir el documento)"

        # --- Preprocesar cada token para que coincida con la consulta ---
        texto_normalizado = []
        for t in texto_original:
            # eliminar puntuación y símbolos sueltos igual que en preprocesar_texto
            t_norm = re.sub(r'[^\w\s-]', '', t.lower())
            t_norm = re.sub(r'(?<!\w)-|-(?!\w)', '', t_norm)
            t_norm = re.sub(r'\b\w*\d+\b', '', t_norm)
            texto_normalizado.append(t_norm)

        palabra_lower = palabra.lower()

        # Buscar primera coincidencia normalizada
        for i, t_norm in enumerate(texto_normalizado):
            if t_norm == palabra_lower:
                inicio = max(0, i - 5)
                fin = min(len(texto_original), i + 10)
                fragmento = texto_original[inicio:fin]

                # resaltar usando la palabra NORMALIZADA
                fragmento_resaltado = []
                for real, norm in zip(fragmento, texto_normalizado[inicio:fin]):
                    if norm == palabra_lower:
                        fragmento_resaltado.append(f"**{real}**")
                    else:
                        fragmento_resaltado.append(real)

                return " ".join(fragmento_resaltado)

        return "(No se encontró un fragmento relevante)"

    # Calcular similitud coseno entre un documento y la consulta
    def calcular_similitud_coseno(self, documento, tokens_consulta):
        # similitud entre el documento (dj) y la consulta (q)
        valor_absoluto_dj = self.vectoresNormales[documento]
        # calcular el valor absoluto del vector de la consulta
        # cuando hablamos de w_iq nos referimos al idf de la palabra i en la consulta q
        sumatorio = 0.0
        for palabra in tokens_consulta:
            if palabra in self.indice:
                sumatorio += (self.indice[palabra][0])**2
        valor_absoluto_q = math.sqrt(sumatorio)
        # calcular el numerador, es decir, el producto escalar entre dj y q
        producto_escalar = 0.0
        for palabra in tokens_consulta:
            if palabra in self.indice:
                tf_idf_dj = 0.0
                if documento in self.indice[palabra][1]:
                    tf_idf_dj = self.indice[palabra][1][documento][0]
                tf_idf_q = self.indice[palabra][0]  # idf de la palabra en la consulta
                producto_escalar += tf_idf_dj * tf_idf_q

        if valor_absoluto_dj == 0.0 or valor_absoluto_q == 0.0:
            return 0.0

        return producto_escalar / (valor_absoluto_dj * valor_absoluto_q)
    
    # Buscar la siguiente aparición de una frase en un texto tokenizado
    # parametros: frase_tokens: lista de terminos de la frase
    #             position: posición desde donde empezar a buscar
    def next_phrase(self, frase_tokens, position = 0):
        """
        Devuelve el índice de inicio y fin de la primera aparición de frase_tokens en texto_tokens
        empezando desde start_pos. Retorna None si no se encuentra.
        """
        n = len(frase_tokens)
        v = position

        # desde i = 1 hasta n hacer
        #    v <- next(ti, v)
        # next(ti, v): Devuelve la siguiente aparición del término ti después de la posición v (o vacio si no hay más)
        for i in range(n):
            v = self.next_term(frase_tokens[i], v)
        if v is None:
            return None
        u = v
        # desde i = n-1 hasta 1 hacer
        for i in range(n-1, -1, -1):
            # prev(ti, u): Devuelve la anterior aparición del término ti antes de la posición u (o vacio si no hay más)
            u = self.prev_term(frase_tokens[i], u)
        if (v-u) == n-1:
            return (u, v)
        else:
            return self.next_phrase(frase_tokens, position = u+1)
    
    def next_term(self, term, position):
        # Devuelve la siguiente aparición del término term después de la posición position (o None si no hay más)
        if term not in self.indice:
            return None
        posiciones = self.indice[term][2]  # lista de posiciones del término en el corpus
        for pos in posiciones:
            if pos > position:
                return pos
        return None
    
    def prev_term(self, term, position):
        # Devuelve la anterior aparición del término term antes de la posición position (o None si no hay más)
        if term not in self.indice:
            return None
        posiciones = self.indice[term][2]  # lista de posiciones del término en el corpus
        for pos in reversed(posiciones):
            if pos < position:
                return pos
        return None
    
    def procesar_Bloques_AND(self, bloques_procesados):
        documentos_candidatos = None
        for bloque in bloques_procesados:
            documentos_bloque = set()
            for termino in bloque:
                if termino in self.indice:
                    documentos_termino = set(self.indice[termino][1].keys())
                    documentos_bloque.update(documentos_termino)
        if documentos_candidatos is None:
            documentos_candidatos = documentos_bloque
        else:
            documentos_candidatos.intersection_update(documentos_bloque)
        return documentos_candidatos
    
    def preprocesar_consulta(self, consulta):
        tokensNL, tokensL = preprocesar_texto(consulta)
        if isinstance(tokensNL, str):
            tokensNL = tokensNL.split()

        if isinstance(tokensL, str):
            tokensL = tokensL.split()
        tokens = tokensL if self.tipoIndice == "1" else tokensNL
        return tokens
    
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
        # 1) Separar la consulta por ANDs
        bloques_and = [bloque.strip() for bloque in consulta.split(" AND ")]
        bloques_procesados = []
        frases_exactas = []
        # 2) 3) 4)
        for bloque in bloques_and:
            # 2) Tratar las comillas dobles como frases exactas
            frases = re.findall(r'"(.*?)"', bloque)
            for frase in frases:
                frases_exactas.append(frase)
            # Eliminar las frases del bloque
            bloque_sin_frases = re.sub(r'"(.*?)"', '', bloque)
            # 3) Remplazar los ORs por " "
            bloque_sin_frases = bloque_sin_frases.replace(" OR ", " ")
            # 4) Preprocesar la consulta según
            bloques_procesados.append(self.preprocesar_consulta(bloque_sin_frases))
        
        # 5) Buscar documentos que cumplan los bloques AND
        documentos_candidatos_and = self.procesar_Bloques_AND(bloques_procesados)
        if not documentos_candidatos_and:
            return None
    
        # 6) Filtrar por frases exactas usando la funcion next_phrase
        for frase in frases_exactas:
            tokens_frase = self.preprocesar_consulta(frase)
            documentos_a_eliminar = set()
            for doc in documentos_candidatos_and:
                encontrado = False
                while True:
                    resultado = self.next_phrase(tokens_frase)
                    if resultado is None:
                        break
                    else:
                        encontrado = True
                        break
                if not encontrado:
                    documentos_a_eliminar.add(doc)
            documentos_candidatos_and.difference_update(documentos_a_eliminar)
            if not documentos_candidatos_and:
                return None
        
        # 7) Calcular similitud coseno y rankear
        tokens_consulta = []
        for bloque in bloques_procesados:
            tokens_consulta.extend(bloque)
        documentos_con_similitud = []
        for doc in documentos_candidatos_and:
            similitud = self.calcular_similitud_coseno(doc, tokens_consulta)
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
            for termino in tokens_consulta:
                fragmento = self.obtener_fragmento(doc, termino)
                print(f"Fragmento: {fragmento}")

        print("\n===== FIN RESULTADOS =====")

        return documentos_ordenados
