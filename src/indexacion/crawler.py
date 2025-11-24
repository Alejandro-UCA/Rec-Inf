import requests
from bs4 import BeautifulSoup

def crawler():
    url = "https://raw.githubusercontent.com/andres-munoz/RECINF-Project/refs/heads/main/index.html"
    try:
        reponse = requests.get(url)
        if reponse.status_code == 200:
            print("Crawling the webpage...")
            soup = BeautifulSoup(reponse.content, 'html.parser')
            enlaces = soup.find_all('a')
            for enlace in enlaces:
                href = enlace.get('href')
                print(href)
                if href is not None:
                    url = url.replace("index.html", href)
                    documento = requests.get(url)
                    if documento.status_code == 200:
                        with open("./corpus/"+href.split("/")[-1], "w", encoding="utf-8") as f:
                            f.write(documento.text + "\n")
                        print(f"Downloaded and saved: {href}")
        else:
            print(f"Error: Unable to fetch the URL. Status code: {reponse.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None