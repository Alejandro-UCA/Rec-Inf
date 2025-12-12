from indexacion import indexacion
import os

# 1. Obtiene la ruta absoluta de la carpeta donde está ESTE archivo (main.py)
ruta_directorio_main = os.path.dirname(os.path.abspath(__file__))

# 2. Le dice a Python: "Muévete a esa carpeta antes de hacer nada más"
os.chdir(ruta_directorio_main)

if __name__ == "__main__":
    # Si no están las dependencias instaladas, instalarlas
    if not os.path.exists("../venv"): # NO SE SI ESTO VA
        print("No se encontraron dependencias. Instalando...")
        os.system("pip install -r ./requirements.txt")
        os.system("python -m spacy download en_core_web_sm")
    
    indexador = indexacion.Indexador() # Crear una instancia de la clase Indexador
    indexador.preProcesar()
    indexador.calcularTF_IDF()
    indexador.mostrarDatos()