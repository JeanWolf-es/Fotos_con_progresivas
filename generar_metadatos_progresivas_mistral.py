# ==============================================================================
# Sistema Unificado de Procesamiento Vial: Metadatos IA, IPTC y Progresivas
# ==============================================================================
# Dependencias: !pip install pandas shapely pyproj pillow iptcinfo3 requests

import os
import sys
import json
import base64
import tempfile
import argparse
import csv
import time
import logging
import traceback
import warnings
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from iptcinfo3 import IPTCInfo
import requests
import pandas as pd
from shapely.geometry import Point, LineString
import pyproj

# --- PARCHE CRÍTICO PARA PYPROJ (Entornos Conda / Jupyter en Windows) ---
conda_prefix = os.environ.get('CONDA_PREFIX', sys.prefix)
posibles_rutas = [
    os.path.join(conda_prefix, 'Library', 'share', 'proj'),
    os.path.join(sys.prefix, 'Library', 'share', 'proj'),
    os.path.join(sys.prefix, 'Lib', 'site-packages', 'pyproj', 'proj_dir', 'share', 'proj')
]
for ruta in posibles_rutas:
    if os.path.exists(os.path.join(ruta, 'proj.db')):
        os.environ['PROJ_LIB'] = ruta
        os.environ['PROJ_DATA'] = ruta
        break

warnings.filterwarnings("ignore", category=UserWarning, module="pyproj")

# --- CONFIGURACIÓN Y CONSTANTES ---
CREDENTIALS_PATH = r"C:\Users\Dell\Downloads\CSS\comprension_word\Metadatos_Mistral.json"
VISION_MODEL = "pixtral-12b-2409"
BUFFER_TOLERANCIA_M = 50.0  # Umbral de desvío máximo permitido en metros respecto al eje

# ==============================================================================
# FASE 1: EXTRACCIÓN DE METADATOS E INTELIGENCIA ARTIFICIAL (MISTRAL VÍA)
# ==============================================================================
def cargar_credenciales():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales: {CREDENTIALS_PATH}")
    with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        api_key = data.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("El archivo JSON no contiene 'MISTRAL_API_KEY'.")
        return api_key

def obtener_exif_data(ruta_imagen):
    fecha = "Fecha desconocida"
    latitud, longitud = "", ""
    try:
        with Image.open(ruta_imagen) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        fecha = value
                
                gps_info = exif_data.get(34853)
                if gps_info:
                    def convertir_a_grados(valor):
                        d = float(valor[0])
                        m = float(valor[1])
                        s = float(valor[2])
                        return d + (m / 60.0) + (s / 3600.0)
                        
                    if 2 in gps_info and 4 in gps_info:
                        lat = convertir_a_grados(gps_info[2])
                        if gps_info.get(1) == 'S': lat = -lat
                        lon = convertir_a_grados(gps_info[4])
                        if gps_info.get(3) == 'W': lon = -lon
                        
                        latitud = str(round(lat, 6))
                        longitud = str(round(lon, 6))
    except Exception as e:
        print(f"⚠️ Error leyendo EXIF de {ruta_imagen}: {e}")
    return fecha, latitud, longitud

def optimizar_imagen(ruta_original, target_min_kb=300, target_max_kb=400):
    """
    Submuestrea temporalmente la imagen para que se ubique estrictamente
    dentro del rango ideal de transmisión de datos (300 KB - 400 KB).
    """
    peso_bytes = os.path.getsize(ruta_original)
    peso_kb = peso_bytes / 1024

    if target_min_kb <= peso_kb <= target_max_kb:
        return ruta_original, peso_kb, peso_kb

    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    
    try:
        with Image.open(ruta_original) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            calidad = 95
            img.save(temp_path, format='JPEG', quality=calidad, optimize=True)
            nuevo_peso = os.path.getsize(temp_path) / 1024
            
            while (nuevo_peso > target_max_kb or nuevo_peso < target_min_kb) and calidad > 15:
                if nuevo_peso > target_max_kb:
                    calidad -= 5
                else:
                    if peso_kb < target_min_kb:
                        break
                    calidad += 2
                    
                img.save(temp_path, format='JPEG', quality=calidad, optimize=True)
                nuevo_peso = os.path.getsize(temp_path) / 1024
                
        peso_final_kb = os.path.getsize(temp_path) / 1024
        return temp_path, peso_kb, peso_final_kb
    except Exception as e:
        print(f"⚠️ Error al optimizar peso de {ruta_original}: {e}")
        return ruta_original, peso_kb, peso_kb

def consultar_vision_mistral(ruta_imagen, api_key, parametro_general):
    with open(ruta_imagen, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = (
        f"Actúa como profecional en obras de carreteras. Toma en cuenta este contexto general: '{parametro_general}'. "
        "Escribe una descripción técnica muy breve (máximo 150 caracteres) sobre lo que se observa en esta imagen de la vía o "
        "los trabajos. Solo devuelve la descripción en español, sin texto adicional."
    )
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                ]
            }
        ]
    }
    
    start_time = datetime.now()
    response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)
    duracion = (datetime.now() - start_time).total_seconds()
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip(), duracion
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

def escribir_iptc(ruta_imagen, descripcion):
    try:
        info = IPTCInfo(ruta_imagen, force=True)
        info['caption/abstract'] = descripcion.encode('latin-1', 'replace')
        info.save()
        if os.path.exists(ruta_imagen + "~"):
            os.remove(ruta_imagen + "~")
        return True
    except Exception as e:
        print(f"⚠️ Error IPTC en {ruta_imagen}: {e}")
        return False

# ==============================================================================
# FASE 2: GEOPROCESAMIENTO DESDE EL CSV LOCAL Y ALINEAMIENTO JSON
# ==============================================================================
def configurar_transformador():
    if 'PROJ_LIB' in os.environ:
        import pyproj.datadir
        pyproj.datadir.set_data_dir(os.environ['PROJ_LIB'])
    return pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True)

def procesar_eje(ruta_eje, transformador):
    if not os.path.exists(ruta_eje):
        raise FileNotFoundError(f"No se encontró el archivo geométrico obligatorio del eje en: {ruta_eje}")
        
    with open(ruta_eje, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        
    if isinstance(datos, dict) and "estaciones" in datos:
        puntos_utm = []
        estaciones = sorted(datos["estaciones"], key=lambda x: x.get("distancia_m", 0))
        
        for est in estaciones:
            if "utm_e" in est and "utm_n" in est:
                puntos_utm.append((float(est["utm_e"]), float(est["utm_n"])))
            else:
                x, y = transformador.transform(float(est["lon"]), float(est["lat"]))
                puntos_utm.append((x, y))
                
        if len(puntos_utm) < 2:
            raise ValueError("El archivo de estaciones no contiene suficientes vértices para trazar una línea.")
            
        return LineString(puntos_utm)
        
    raise ValueError(f"La estructura interna de '{os.path.basename(ruta_eje)}' no cuenta con el arreglo 'estaciones' requerido.")

def formatear_progresiva(distancia_m):
    distancia_entera = int(round(distancia_m))
    return f"{distancia_entera // 1000}+{distancia_entera % 1000:03d}"

def calcular_progresivas_en_csv(ruta_csv, eje_vial, transformador):
    """Calcula las progresivas espaciales directamente desde el CSV ya generado."""
    df = pd.read_csv(ruta_csv)
    
    if 'Latitud' not in df.columns or 'Longitud' not in df.columns:
        raise ValueError("El archivo CSV no posee las columnas geográficas obligatorias 'Latitud' y 'Longitud'.")
        
    df['PROGRESIVA'] = pd.NA
    puntos_ok, puntos_out = 0, 0
    
    for idx, row in df.iterrows():
        lat = row['Latitud']
        lon = row['Longitud']
        
        if pd.isna(lat) or pd.isna(lon) or str(lat).strip() == "" or str(lon).strip() == "":
            continue
            
        x_utm, y_utm = transformador.transform(float(lon), float(lat))
        punto_utm = Point(x_utm, y_utm)
        distancia_ortogonal = punto_utm.distance(eje_vial)
        
        if distancia_ortogonal <= BUFFER_TOLERANCIA_M:
            distancia_acumulada = eje_vial.project(punto_utm)
            df.at[idx, 'PROGRESIVA'] = formatear_progresiva(distancia_acumulada)
            puntos_ok += 1
        else:
            puntos_out += 1
            
    # Reordenación de columnas para que PROGRESIVA quede al lado de Longitud
    columnas = list(df.columns)
    if 'PROGRESIVA' in columnas:
        columnas.remove('PROGRESIVA')
        idx_insercion = columnas.index('Longitud') + 1 if 'Longitud' in columnas else 5
        columnas.insert(idx_insercion, 'PROGRESIVA')
        df = df.reindex(columns=columnas)
        
    df.to_csv(ruta_csv, index=False, encoding='utf-8-sig')
    print(f"📊 Resumen Espacial (Buffer {BUFFER_TOLERANCIA_M}m):")
    print(f"   ↳ Puntos acoplados a la vía   : {puntos_ok}")
    print(f"   ↳ Puntos fuera de rango (>50m): {puntos_out}")

# ==============================================================================
# ORQUESTADOR PRINCIPAL DEL FLUJO COMPLETO
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Procesamiento unificado de fotos e indexación de progresivas desde CSV.")
    parser.add_argument("carpeta", nargs='?', help="Ruta de la carpeta origen con las imágenes.")
    args = parser.parse_args()
    
    carpeta_fotos = args.carpeta if args.carpeta else input("Por favor, arrastra la carpeta con las FOTOS aquí: ").strip()
    carpeta_fotos = carpeta_fotos.strip('"\' ')

    if not os.path.isdir(carpeta_fotos):
        print(f"❌ Error: La ruta '{carpeta_fotos}' no es un directorio válido.")
        sys.exit(1)

    # Definición de rutas absolutas locales fijas (Carpeta del Script)
    dir_local = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(dir_local, "metadatos_mensual.csv")
    ruta_json_eje = os.path.join(dir_local, "progresivas.json")
    log_file = os.path.join(dir_local, "error_progresivas.log")

    archivos_imagen = []
    for root, _, files in os.walk(carpeta_fotos):
        for f in files:
            if os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg'}:
                archivos_imagen.append(os.path.join(root, f))
                
    if not archivos_imagen:
        print("⚠️ No se encontraron imágenes JPG/JPEG en el directorio de fotos proporcionado.")
        sys.exit(0)

    print("-" * 60)
    print(f"📁 Directorio del Script (Salida CSV) : {dir_local}")
    print(f"📸 Directorio de Origen de Fotos       : {carpeta_fotos}")
    print(f"🗺️ Trazado Geométrico Vial             : {os.path.basename(ruta_json_eje)}")
    print("-" * 60)

    # --------------------------------------------------------------------------
    # EJECUCIÓN FASE 1: CONEXIÓN CON IA Y GENERACIÓN DEL CSV LOCAL
    # --------------------------------------------------------------------------
    print(f"\n🚀 [INICIANDO FASE 1]: Procesando {len(archivos_imagen)} imágenes con Mistral IA...")
    try:
        api_key = cargar_credenciales()
    except Exception as e:
        print(f"❌ Error cargando credenciales: {e}")
        sys.exit(1)
        
    parametro_general = input("📝 Ingresa la descripción/parámetro general para este set de fotos: ").strip()
    resultados = []
    
    for i, ruta in enumerate(archivos_imagen):
        if i > 0:
            time.sleep(0.7)
            
        nombre = os.path.basename(ruta)
        fecha_exif, lat, lon = obtener_exif_data(ruta)
        ruta_temporal = None
        
        try:
            ruta_evaluada, peso_orig, peso_final = optimizar_imagen(ruta)
            if ruta_evaluada != ruta:
                ruta_temporal = ruta_evaluada
                
            descripcion, tiempo_api = consultar_vision_mistral(ruta_evaluada, api_key, parametro_general)
            escribir_iptc(ruta, descripcion)
            estado = "OK"
        except Exception as e:
            descripcion = f"ERROR: {str(e)}"
            estado = "Error FASE 1"
            peso_orig, peso_final, tiempo_api = 0, 0, 0
        finally:
            if ruta_temporal and os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
                
        resultados.append({
            "Nombre": nombre, "DIR": ruta, "FECHA": fecha_exif, "Latitud": lat, "Longitud": lon,
            "Descripción": descripcion, "Estado": estado, "Peso Original (KB)": round(peso_orig, 2),
            "Peso Enviado (KB)": round(peso_final, 2), "Tiempo API (s)": round(tiempo_api, 2)
        })
        print(f"   ↳ [📸 Procesada] {nombre} | Peso Enviado: {round(peso_final, 2)} KB | Estado: {estado}")

    # Escritura inicial del CSV en la carpeta del script
    try:
        campos = ["Nombre", "DIR", "FECHA", "Latitud", "Longitud", "Descripción", "Estado", "Peso Original (KB)", "Peso Enviado (KB)", "Tiempo API (s)"]
        with open(ruta_csv, mode='w', newline='', encoding='utf-8') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=campos)
            writer.writeheader()
            for r in resultados:
                writer.writerow(r)
        print(f"✅ Fase 1 completada con éxito. Archivo base generado en: {ruta_csv}")
    except Exception as e:
        print(f"❌ Error crítico guardando el CSV base: {e}")
        sys.exit(1)

    # --------------------------------------------------------------------------
    # EJECUCIÓN FASE 2: GEOPROCESAMIENTO DESDE EL CSV GENERADO
    # --------------------------------------------------------------------------
    print(f"\n🛰️ [INICIANDO FASE 2]: Extrayendo datos del CSV para el cálculo de PROGRESIVAS...")
    logging.basicConfig(filename=log_file, level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
    try:
        transformador_crs = configurar_transformador()
        eje_metrico = procesar_eje(ruta_json_eje, transformador_crs)
        print("   ↳ Geometría del eje vial cargada correctamente.")
        
        # El cálculo lee e inyecta la progresiva analizando el archivo CSV
        calcular_progresivas_en_csv(ruta_csv, eje_metrico, transformador_crs)
        print(f"\n🚀 Proceso unificado completado con éxito.")
        print(f"📄 Reporte final con progresivas actualizado en: {ruta_csv}")
    except Exception as e:
        error_msg = traceback.format_exc()
        logging.error(f"Fallo crítico en el procesamiento espacial de la Fase 2:\n{error_msg}")
        print(f"❌ Error en la Fase 2 de geoprocesamiento. Los detalles se guardaron en: {log_file}")

if __name__ == "__main__":
    main()