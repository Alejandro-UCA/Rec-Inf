import os
import requests
from bs4 import BeautifulSoup

def crawler():
    # URL base original
    base_url = "https://raw.githubusercontent.com/andres-munoz/RECINF-Project/refs/heads/main/index.html"
    output_dir = "./corpus/"

    # Asegurarnos de que la carpeta existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("Crawleando la pagina...")
            soup = BeautifulSoup(response.content, 'html.parser')
            enlaces = soup.find_all('a')
            
            for enlace in enlaces:
                href = enlace.get('href')
                
                if href is not None:
                    # Definimos el nombre del archivo y su ruta completa
                    nombre_archivo = href.split("/")[-1]
                    ruta_completa = os.path.join(output_dir, nombre_archivo)

                    if os.path.exists(ruta_completa):
                        print(f"El archivo '{nombre_archivo}' ya existe. Saltando descarga.")
                        continue

                    print(f"Descargando: {href}")
                    
                    # Construimos la URL de descarga sin modificar la base_url original
                    download_url = base_url.replace("index.html", href)
                    
                    documento = requests.get(download_url)
                    
                    if documento.status_code == 200:
                        with open(ruta_completa, "w", encoding="utf-8") as f:
                            f.write(documento.text + "\n")
                        print(f"Guardado exitosamente en: {ruta_completa}")
                    else:
                        print(f"Error al descargar documento: {documento.status_code}")

        else:
            print(f"Error: Unable to fetch the URL. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Excepción: {e}")
        return None