import re
import spacy

nlp = spacy.load("en_core_web_sm") # Este es el modelo en inglés

def preprocesar_consulta(consulta, modo):
    consulta = consulta.lower() #Importante que todo este en minusculas

    expresion_regular = r'("[^"]+"|\S+)'

    tokens = re.findall(expresion_regular, consulta)

    bloques_consulta = [] #La lista de bloques que se deben de procesar en la consulta
                        #Al final, esto será una lista de bloques que se tratan como consultas separadas
                        #Luego la consulta final es un AND entre todos estos bloques
    bloque_actual = [] #Bloque que estamos construyendo

    tokens_reales = [] #La lista de los tokens reales que hay, o sea la lista de "palabras" convalor

    for token in tokens:
        if token == 'and': #El AND sirve como separador de bloques
            if bloque_actual: #Si el bloque que estamos construyendo no esta vacio 
                bloques_consulta.append(bloque_actual) #Se añade a la lista de bloques
                bloque_actual = [] #Reinicio de bloque actual
        
        elif token == 'or':
            continue #El OR en si es irrelevante, se puede poner en la consulta pero no tiene un efecto propio

        else:
            #Llegados a este punto, pueden pasar 2 cosas gracias a la expresion regular:
            #1. Que el token sea una frase entre comillas
            #2. Que el token sea una palabra suelta
            #En ambos casos, esa palabra o frase va a constituir un termino del bloque actual
            termino = token.strip('"') #Quitamos las comillas si las hay
            if modo == '1':
                doc = nlp(termino)
                token = ' '.join([t.lemma_ for t in doc]) #Lematizamos el termino
            tokens_reales.append(token) #Añadimos el token a la lista de tokens reales
            bloque_actual.append(token) #Añadimos el token al bloque actual
        
    if bloque_actual: #Hay que tratar esta ultima a parte, ya que realmente el ultimo bloque
        #no se va a cerrar con un AND el 99% de las veces
        bloques_consulta.append(bloque_actual)
    
    return bloques_consulta, tokens_reales #Devolvemos la lista de bloques de la consulta y la lista de tokens reales

#Ejemplo de uso
if __name__ == "__main__":
    consulta = '"ai generated" or casa and vida'
    bloques, tokens = preprocesar_consulta(consulta)
    print(bloques)
    print("Bloques de la consulta procesada:")
    for i, bloque in enumerate(bloques):
        print(f"Bloque {i+1}: {bloque} {len(bloque)} términos")
        for termino in bloque:
            print(f" - Término: {termino} (Numero de palabras: {len(termino.split())})")
    print("Tokens reales:")
    print(tokens)
    for token in tokens:
        print(f" - {token}")