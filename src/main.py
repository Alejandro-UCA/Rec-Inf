from indexacion import indexacion
import os

# 1. Obtiene la ruta absoluta de la carpeta donde está ESTE archivo (main.py)
ruta_directorio_main = os.path.dirname(os.path.abspath(__file__))

# 2. Le dice a Python: "Muévete a esa carpeta antes de hacer nada más"
os.chdir(ruta_directorio_main)

if __name__ == "__main__":
    indexacion.indexacion()