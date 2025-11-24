from . import preProcesado
from . import tratarTexto
from . import mostrarDatos
import json

class Indexador:
    def __init__(self):
        self.indiceLm = {} #{str: [int, dict{str: [int, [int]}]} -> Por cada token guardamos su IDF y una lista de los
                            #documentos donde aparece y por cada documento su TF-IDF y las posiciones donde aparece
        self.indiceNoLm = {}
        self.vectoresNormalesLm = {}
        self.vectoresNormalesNoLm = {}

    def preProcesar(self):
        preProcesado.preProcesamiento()

    def calcularTF_IDF(self, textoPreProcesado = None):
        self.indiceLm, self.indiceNoLm, self.vectoresNormalesLm, self.vectoresNormalesNoLm \
            = tratarTexto.tf_idf(self.indiceLm, self.indiceNoLm, textoPreProcesado)
        with open("./resultados/indiceLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.indiceLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/indiceNoLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.indiceNoLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/vectoresNormalesLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.vectoresNormalesLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/vectoresNormalesNoLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.vectoresNormalesNoLm, f, ensure_ascii=False, indent=4)
    
    def cargarIndices(self):
        with open("./resultados/indiceLematizado.json", "r", encoding="utf-8") as f:
            self.indiceLm = json.load(f)
        with open("./resultados/indiceNoLematizado.json", "r", encoding="utf-8") as f:
            self.indiceNoLm = json.load(f)
        with open("./resultados/vectoresNormalesLematizado.json", "r", encoding="utf-8") as f:
            self.vectoresNormalesLm = json.load(f)
        with open("./resultados/vectoresNormalesNoLematizado.json", "r", encoding="utf-8") as f:
            self.vectoresNormalesNoLm = json.load(f)
    
    def mostrarDatos(self):
        mostrarDatos.mostrarDatos()