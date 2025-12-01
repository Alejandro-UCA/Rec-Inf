from . import preProcesado
from . import tratarTexto
from . import mostrarDatos
import json

class Indexador:
    def __init__(self):
        self.indiceLm = {}
        self.indiceNoLm = {}
        # {str: [int, dict{str: [int, [int]}]} -> Por cada token guardamos su IDF y una lista de los
        # documentos donde aparece y por cada documento su TF-IDF y las posiciones donde aparece
        self.vectoresNormalesLm = {}
        self.vectoresNormalesNoLm = {}

    def preProcesar(self):
        preProcesado.preProcesamiento()

    # Calcula el TF-IDF de los documentos preprocesados y guarda los índices y vectores normales en archivos JSON
    def calcularTF_IDF(self, textoPreProcesado = None):
        self.indiceLm, self.indiceNoLm, self.vectoresNormalesLm, self.vectoresNormalesNoLm \
            = tratarTexto.tf_idf(textoPreProcesado)
        with open("./resultados/indiceLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.indiceLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/indiceNoLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.indiceNoLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/vectoresNormalesLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.vectoresNormalesLm, f, ensure_ascii=False, indent=4)
        with open("./resultados/vectoresNormalesNoLematizado.json", "w", encoding="utf-8") as f:
            json.dump(self.vectoresNormalesNoLm, f, ensure_ascii=False, indent=4)

    # Muestra los datos de los índices y vectores normales
    def mostrarDatos(self):
        mostrarDatos.mostrarDatos()