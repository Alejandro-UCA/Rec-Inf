from busqueda import busqueda
import os

# 1. Obtiene la ruta absoluta de la carpeta donde está ESTE archivo (main.py)
ruta_directorio_main = os.path.dirname(os.path.abspath(__file__))

# 2. Le dice a Python: "Muévete a esa carpeta antes de hacer nada más"
os.chdir(ruta_directorio_main)

if __name__ == "__main__":
    # Iniciar búsqueda
    buscador = busqueda.Buscador() # Crear una instancia de la clase Buscador
    buscador.pedirTipoIndice()
    buscador.cargarIndices()
    buscador.pedirTopN()
    if not buscador.indice or not buscador.vectoresNormales:
        print("No se pudieron cargar los índices. Saliendo del programa.")
        exit(1)
    while exit := input("¿Desea realizar una búsqueda? (s/n): ").lower() == 's':
        documentos = buscador.pedirConsulta()
        if documentos is None:
            print("No se encontraron documentos o la consulta fue vacía.")

        