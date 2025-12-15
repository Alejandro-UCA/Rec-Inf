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
    def calcular_similitud_coseno(self, documento, consulta, indice):
        # similitud entre el documento (dj) y la consulta (q)
        valor_absoluto_dj = self.vectoresNormales[documento]
        # calcular el valor absoluto del vector de la consulta
        # cuando hablamos de w_iq nos referimos al idf de la palabra i en la consulta q
        sumatorio = 0.0
        for palabra in consulta:
            sumatorio += (indice[palabra][0])**2
        valor_absoluto_q = math.sqrt(sumatorio)
        # calcular el numerador, es decir, el producto escalar entre dj y q
        producto_escalar = 0.0
        for palabra in consulta:
            tf_idf_dj = 0.0
            if documento in indice[palabra][1]:
                tf_idf_dj = indice[palabra][1][documento][0]
            tf_idf_q = indice[palabra][0]  # idf de la palabra en la consulta
            producto_escalar += tf_idf_dj * tf_idf_q

        if valor_absoluto_dj == 0.0 or valor_absoluto_q == 0.0:
            return 0.0

        return producto_escalar / (valor_absoluto_dj * valor_absoluto_q)
    
    # Buscar la siguiente aparición de una frase en un texto tokenizado
    def next_phrase(self, texto_tokens, frase_tokens, start_pos=0):
        """
        Devuelve el índice de inicio y fin de la primera aparición de frase_tokens en texto_tokens
        empezando desde start_pos. Retorna None si no se encuentra.
        """
        n = len(frase_tokens)
        v = start_pos

        while v < len(texto_tokens):
            # Buscar primer token de la frase
            try:
                v = texto_tokens.index(frase_tokens[0], v)
            except ValueError:
                return None  # no se encuentra

            # Verificar secuencia completa
            u = v
            match = True
            for i in range(n):
                if v + i >= len(texto_tokens) or texto_tokens[v + i] != frase_tokens[i]:
                    match = False
                    break
            if match:
                return (u, u + n - 1)  # posiciones inicio-fin de la frase
            v += 1  # avanzar y buscar siguiente posible inicio

        return None
    # Verificar si un documento contiene una frase exacta
    def documento_contiene_frase(self, documento, frase_tokens):
        """
        Devuelve True si el documento contiene la frase EXACTA consecutiva,
        usando la misma normalización que el índice.
        """
        try:
            with open(f"./corpus/{documento}", "r", encoding="utf-8") as f:
                texto = f.read()
        except FileNotFoundError:
            return False

        # Preprocesar documento según el tipo de índice
        sinLen, conLen = preprocesar_texto(texto)
        texto_tokens = conLen if self.tipoIndice == "1" else sinLen

        # Preprocesar también la frase con el mismo método
        frase_str = " ".join(frase_tokens)
        frase_sin, frase_con = preprocesar_texto(frase_str)
        frase_proc = frase_con if self.tipoIndice == "1" else frase_sin

        n = len(frase_proc)
        for i in range(len(texto_tokens) - n + 1):
            if texto_tokens[i:i+n] == frase_proc:
                return True

        return False


    # Analizar la consulta en bloques AND y términos/frases
    def parsear_consulta(self, consulta):
        # Devuelve una lista de bloques AND, donde cada bloque es una lista de términos o frases.
        # Extraer frases entre comillas
        frases = re.findall(r'"([^"]+)"', consulta)

        # Reemplazarlas por marcadores
        consulta_tmp = consulta
        mapa_frases = {}
        for i, frase in enumerate(frases):
            key = f"__FRASE_{i}__"
            mapa_frases[key] = frase
            consulta_tmp = consulta_tmp.replace(f'"{frase}"', key)

        # Separar por AND
        bloques_and = re.split(r'\s+AND\s+|\s+and\s+', consulta_tmp)

        resultado = []

        for bloque in bloques_and:
            tokens = bloque.split()
            elementos = []
            for t in tokens:
                if t in mapa_frases:
                    # frase exacta
                    frase_tokens = mapa_frases[t].split()
                    elementos.append({
                        "tipo": "frase",
                        "valor": frase_tokens
                    })
                elif t.upper() != "OR":
                    elementos.append({
                        "tipo": "termino",
                        "valor": t
                    })
            resultado.append(elementos)

        return resultado

    # Funcion que maneja las consultas default, las OR y las AND
    def buscar_y_rankear(self):
        """
        Busca documentos asegurando que:
        - todas las frases exactas aparezcan consecutivamente en el documento
        - solo documentos que cumplan todas las frases entran al ranking
        - si hay términos sueltos, se usan para ranking TF-IDF, pero no permiten que documentos que no contienen la frase entren
        """
        # Obtener la consulta como string
        consulta_str = self.consulta if isinstance(self.consulta, str) else " ".join(self.consulta)
        bloques_and = self.parsear_consulta(consulta_str)

        documentos_candidatos = None
        tokens_consulta = []
        frases_consulta = []

        # Extraer términos y frases de la consulta
        for bloque in bloques_and:
            docs_bloque = set()
            for elem in bloque:
                if elem["tipo"] == "termino":
                    palabra = elem["valor"]
                    tokens_consulta.append(palabra)
                    if palabra in self.indice:
                        docs_bloque |= set(self.indice[palabra][1].keys())
                else:
                    frases_consulta.append(elem["valor"])
            documentos_candidatos = docs_bloque if documentos_candidatos is None else documentos_candidatos & docs_bloque

        # Si no hay términos sueltos, considerar todos los documentos
        if not tokens_consulta:
            documentos_candidatos = set(self.vectoresNormales.keys())

        if not documentos_candidatos:
            print("No existen documentos relevantes para esta consulta.")
            return None, None

        # FILTRADO ESTRICTO: solo documentos que contengan TODAS las frases consecutivas
        documentos_finales = set()
        for doc in documentos_candidatos:
            cumple = True
            for frase in frases_consulta:
                if not self.documento_contiene_frase(doc, frase):
                    cumple = False
                    break
            if cumple:
                documentos_finales.add(doc)

        if not documentos_finales:
            print("No hay documentos que contengan las frases exactas.")
            return None, None

        # Ranking por TF-IDF solo sobre términos sueltos (si hay)
        ranking_documentos = {}
        for doc in documentos_finales:
            if tokens_consulta:
                ranking_documentos[doc] = self.calcular_similitud_coseno(doc, tokens_consulta, self.indice)
            else:
                ranking_documentos[doc] = 1.0  # si no hay términos, score fijo para mostrar

        return ranking_documentos, tokens_consulta


    # Pedir consulta al usuario y procesarla
    def pedirConsulta(self):
        consulta = input("Ingrese su consulta: ")
        print(f"Consulta recibida: {consulta}")
        
        if consulta.strip() == "":
            print("Consulta vacía. Por favor, ingrese una consulta válida.")
            return None
        
        # preprocesar_texto devuelve una TUPLA (sin_lematizar, lematizado)
        sinLen, conLen = preprocesar_texto(consulta)
        if self.tipoIndice == "1":
            self.consulta = conLen
        else:
            self.consulta = sinLen
        
        ranking_documentos, tokens_consulta = self.buscar_y_rankear()

        if ranking_documentos is None or tokens_consulta is None:
            return None
            
        # Ordenar por similitud descendente
        ranking_documentos = dict(sorted(ranking_documentos.items(), key=lambda item: item[1], reverse=True))
        # Limitar a los N primeros
        documentos_ordenados = list(ranking_documentos.items())[:self.top_n]

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
