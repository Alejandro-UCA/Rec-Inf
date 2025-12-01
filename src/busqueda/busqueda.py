import json
from src.indexacion.preProcesado import preprocesar_texto
class Buscador:
    def __init__(self):
        self.indice = {}
        self.vectoresNormales = {}
        self.consulta = ""
        self.tipoIndice = ""
    
    # pedirTipoIndice: Pregunta al usuario qué tipo de índice desea usar
    def pedirTipoIndice(self):
        print("¿Desea usar los indices Lematizados (1) o No Lematizados (2)?")
        self.tipoIndice = input("Ingrese 1 o 2: ")
        if self.tipoIndice not in ["1", "2"]:
            print("Opción inválida. Usando índice Lematizado por defecto.")
            self.tipoIndice = "1"
    
    # Cargar en memoria los indices y los vectores normales    
    def cargarIndices(self):
        if self.tipoIndice == "1":
            print("Cargando índices Lematizados...")
            with open("../resultados/indiceLematizado.json", "r", encoding="utf-8") as f:
                self.indice = json.load(f)
            with open("../resultados/vectoresNormalesLematizado.json", "r", encoding="utf-8") as f:
                self.vectoresNormales = json.load(f)
        elif self.tipoIndice == "2":
            print("Cargando índices No Lematizados...")
            with open("../resultados/indiceNoLematizado.json", "r", encoding="utf-8") as f:
                self.indice = json.load(f)
            with open("../resultados/vectoresNormalesNoLematizado.json", "r", encoding="utf-8") as f:
                self.vectoresNormales = json.load(f)

    # Pedir consulta al usuario y preprocesarla
    def pedirConsulta(self):
        consulta = input("Ingrese su consulta: ")
        print(f"Consulta recibida: {consulta}")
        if consulta.strip() == "":
            print("Consulta vacía. Por favor, ingrese una consulta válida.")
            return None
        consultaIni = preprocesar_texto(consulta)
        if self.tipoIndice == "1":
            self.consulta = consultaIni['textoLematizado']
        else:
            self.consulta = consultaIni['textoSinLematizar']
        
        # Recuperar los documentos que contienen los términos de la consulta
        documentos_encontrados = set()
        for palabra in self.consulta:
            if palabra in self.indice:
                documentos_palabra = self.indice[palabra][1].keys()
                documentos_encontrados.update(documentos_palabra)
                
        # Calcular el ranking de los documentos encontrados 
        ranking_documentos = {}
        for documento in documentos_encontrados:
            ranking_documentos[documento] = 0
            for palabra in self.consulta:
                if palabra in self.indice and documento in self.indice[palabra][1]:
                    tf_idf = self.indice[palabra][1][documento][0]
                    ranking_documentos[documento] += tf_idf
        
        return list(documentos_encontrados)
        