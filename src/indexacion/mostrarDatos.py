import json
import os

# --- ESTILOS CSS ---
ESTILO_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; margin: 20px; background-color: #f9f9f9; }
    h2 { color: #333; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
    table { border-collapse: collapse; width: 100%; background-color: white; table-layout: fixed; }
    th { background-color: #007BFF; color: white; padding: 10px; text-align: left; }
    td { border-bottom: 1px solid #ddd; padding: 8px; vertical-align: top; word-wrap: break-word; }
    tr:hover { background-color: #f1f1f1; }
    
    /* Anchos específicos para las tablas */
    th:nth-child(1) { width: 20%; } /* Columna ID/Término */
    
    .details-box { max-height: 200px; overflow-y: auto; }
    ul { list-style-type: none; padding: 0; margin: 0; }
    li { margin-bottom: 5px; border-bottom: 1px dotted #eee; padding-bottom: 5px; }
    .doc-id { font-weight: bold; color: #2c3e50; }
    .weight { color: #e67e22; font-size: 0.9em; }
    .pos-tag { font-size: 0.85em; color: #7f8c8d; display: block; }
    
    /* Estilo para diferencias en vectores */
    .diff { font-size: 0.85em; color: #888; font-style: italic; }
</style>
"""

def _escribir_header_html(f, titulo, columnas):
    """Escribe el inicio del archivo HTML con columnas dinámicas"""
    f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>{titulo}</title>{ESTILO_CSS}</head><body>")
    f.write(f"<h2>{titulo}</h2>")
    f.write("<table><thead><tr>")
    for col in columnas:
        f.write(f"<th>{col}</th>")
    f.write("</tr></thead><tbody>")

def _escribir_footer_html(f):
    f.write("</tbody></table></body></html>")

def _procesar_y_guardar_indice(json_data, ruta_salida, titulo, limite):
    """Procesa los índices invertidos (Término -> Documentos)"""
    print(f"Generando reporte: {titulo} (Límite: {limite})...")
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        _escribir_header_html(f, f"{titulo} (Top {limite})", ["Término", "Peso Global", "Detalles"])
        
        for i, (termino, valores) in enumerate(json_data.items()):
            if i >= limite: break
                
            peso_global = valores[0]
            docs_dict = valores[1]
            
            html_detalles = "<div class='details-box'><ul>"
            docs_ordenados = sorted(docs_dict.items(), key=lambda x: x[1][0], reverse=True)
            
            for doc_id, doc_info in docs_ordenados:
                peso_doc = doc_info[0]
                posiciones = doc_info[1]
                str_pos = str(posiciones)
                if len(str_pos) > 150: str_pos = str_pos[:150] + "..."
                
                html_detalles += f"""<li><span class="doc-id">📄 {doc_id}</span> <span class="weight">({peso_doc:.4f})</span><span class="pos-tag">Pos: {str_pos}</span></li>"""
            
            html_detalles += "</ul></div>"
            f.write(f"<tr><td><strong>{termino}</strong></td><td>{peso_global:.4f}</td><td>{html_detalles}</td></tr>")
            
        _escribir_footer_html(f)
    print(f"✅ Guardado: {ruta_salida}")

def _procesar_y_guardar_vectores(vec_lem, vec_nolem, ruta_salida, limite):
    """
    NUEVA FUNCIÓN: Crea una tabla comparativa de vectores.
    Combina ambos JSONs basándose en el ID del documento.
    """
    print(f"Generando reporte de Vectores (Límite: {limite})...")
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        _escribir_header_html(f, f"Normas de Vectores (Top {limite})", ["Documento ID", "Norma Lematizada", "Norma No Lematizada"])
        
        # Usamos las claves de uno de los archivos (asumiendo que contienen los mismos docs)
        # Si pueden ser distintos, habría que hacer un set(keys1) | set(keys2)
        ids_documentos = list(vec_lem.keys())
        
        for i, doc_id in enumerate(ids_documentos):
            if i >= limite: break
            
            val_lem = vec_lem.get(doc_id, 0.0)
            val_nolem = vec_nolem.get(doc_id, 0.0)
            
            f.write(f"<tr><td><strong>{doc_id}</strong></td><td>{val_lem:.6f}</td><td>{val_nolem:.6f}</td></tr>")
            
        _escribir_footer_html(f)
    print(f"✅ Guardado: {ruta_salida}")

def mostrarDatos(corpus=None, limite=20):
    base_dir = "./resultados/"
    
    # 1. Cargar Corpus
    ruta_corpus = os.path.join(base_dir, "textoPreProcesado.json")
    if not corpus and os.path.exists(ruta_corpus):
        with open(ruta_corpus, "r", encoding="utf-8") as f: corpus = json.load(f)
    
    if corpus:
        print(f"Generando reporte del Corpus (Límite: {limite})...")
        with open(os.path.join(base_dir, "corpus.html"), "w", encoding="utf-8") as f:
            _escribir_header_html(f, f"Corpus (Top {limite})", ["ID", "Vista Previa", "Palabras"])
            for i, (doc_id, contenido) in enumerate(corpus.items()):
                if i >= limite: break
                txt = contenido.get("lematizado", "")
                preview = (txt[:100] + "...") if len(txt) > 100 else txt
                count = len(contenido.get("sin_lematizar", "").split())
                f.write(f"<tr><td>{doc_id}</td><td>{preview}</td><td>{count}</td></tr>")
            _escribir_footer_html(f)

    # 2. Procesar Índices (Streaming con memoria eficiente)
    files_indices = [
        ("indiceLematizado.json", "indiceLematizado.html", "Índice Lematizado"),
        ("indiceNoLematizado.json", "indiceNoLematizado.html", "Índice No Lematizado")
    ]
    
    for f_in, f_out, titulo in files_indices:
        path = os.path.join(base_dir, f_in)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            _procesar_y_guardar_indice(data, os.path.join(base_dir, f_out), titulo, limite)
            del data

    # 3. NUEVO: Procesar Vectores Normales
    ruta_vec_lem = os.path.join(base_dir, "vectoresNormalesLematizado.json")
    ruta_vec_nolem = os.path.join(base_dir, "vectoresNormalesNoLematizado.json")
    
    if os.path.exists(ruta_vec_lem) and os.path.exists(ruta_vec_nolem):
        with open(ruta_vec_lem, "r", encoding="utf-8") as f: v_lem = json.load(f)
        with open(ruta_vec_nolem, "r", encoding="utf-8") as f: v_nolem = json.load(f)
        
        _procesar_y_guardar_vectores(v_lem, v_nolem, os.path.join(base_dir, "reporte_vectores.html"), limite)
        
        del v_lem, v_nolem
    else:
        print("⚠️ No se encontraron los archivos de vectores para generar su reporte.")

    print("\n¡Todos los procesos finalizados!")