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
        self.top_n = 20    # Número de resultados a mostrar por defecto
    
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

    def calcular_similitud_coseno_OR(self, documento, consulta, indice):
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
    
    def calcular_similitud_coseno_AND(self, documento, consulta, indice):
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
            else :
                return 0.0  # Si falta alguna palabra, la similitud es 0
            tf_idf_q = indice[palabra][0]  # idf de la palabra en la consulta
            producto_escalar += tf_idf_dj * tf_idf_q

        if valor_absoluto_dj == 0.0 or valor_absoluto_q == 0.0:
            return 0.0
        
        return producto_escalar / (valor_absoluto_dj * valor_absoluto_q)
        
    def pedirConsulta(self):
        consulta = input("Ingrese su consulta: ")
        print(f"Consulta recibida: {consulta}")
        
        if consulta.strip() == "":
            print("Consulta vacía. Por favor, ingrese una consulta válida.")
            return None
        
        # preprocesar_texto devuelve una TUPLA (sin_lematizar, lematizado)
        consultaIni = preprocesar_texto(consulta)
        textoSinLematizar, textoLematizado = consultaIni

        # Elegimos según índice
        if self.tipoIndice == "1":
            self.consulta = textoLematizado
        else:
            self.consulta = textoSinLematizar

        # Asegurarse de que self.consulta sea una lista de palabras
        if isinstance(self.consulta, str):
            self.consulta = self.consulta.split()  # separar por espacios

        # Recuperar documentos relevantes
        documentos_encontrados = set()
        for palabra in self.consulta:
            if palabra in self.indice:
                documentos_palabra = self.indice[palabra][1].keys()
                documentos_encontrados.update(documentos_palabra)
        
        if not documentos_encontrados:
            print("No existen documentos relevantes para esta consulta.")
            return None

        # Ranking de documentos usando similitud coseno
        ranking_documentos = {}
        for documento in documentos_encontrados:
            ranking_documentos[documento] = self.calcular_similitud_coseno_OR(documento, self.consulta, self.indice)

        # Ordenar por similitud descendente
        ranking_documentos = dict(sorted(ranking_documentos.items(), key=lambda item: item[1], reverse=True))
        # Limitar a los N primeros
        documentos_ordenados = list(ranking_documentos.items())[:self.top_n]

        # Mostrar resultados
        print("\n===== RESULTADOS DEL RANKING =====")
        for doc, score in documentos_ordenados:
            print(f"\nDocumento: {doc}")
            print(f"Ranking: {score:.4f}")

            # Mostrar fragmento del primer término de la consulta
            termino = self.consulta[0]
            fragmento = self.obtener_fragmento(doc, termino)
            print(f"Fragmento: {fragmento}")

        print("\n===== FIN RESULTADOS =====")

        return documentos_ordenados
