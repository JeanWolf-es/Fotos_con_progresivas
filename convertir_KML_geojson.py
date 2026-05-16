#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
convertir_geojson_a_formato.py
Convierte archivos GeoJSON de Google Earth al formato requerido por el sistema vial.

Uso:
    python convertir_geojson_a_formato.py entrada.geojson salida.json
    python convertir_geojson_a_formato.py --help
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from pyproj import Transformer


def configurar_zona_utm(zona=19, hemisferio='S'):
    """
    Configura la zona UTM para la proyección.
    
    Args:
        zona: Número de zona UTM (1-60)
        hemisferio: 'N' para norte, 'S' para sur
    
    Returns:
        str: Código EPSG para la zona UTM
    """
    hemisferio_codigo = 6 if hemisferio == 'N' else 7
    epsg = f"326{hemisferio_codigo}{zona:02d}" if zona < 10 else f"32{hemisferio_codigo}{zona}"
    return f"EPSG:{epsg}"


def detectar_zona_utm(longitud):
    """
    Detecta la zona UTM basada en la longitud.
    
    Args:
        longitud: Longitud en grados decimales
    
    Returns:
        int: Número de zona UTM
    """
    return int((longitud + 180) / 6) + 1


def generar_json_simplificado(input_path, output_path, zona=19, hemisferio='S', auto_zona=False):
    """
    Convierte un GeoJSON de Google Earth al formato requerido.
    
    Args:
        input_path: Ruta del archivo GeoJSON de entrada
        output_path: Ruta del archivo JSON de salida
        zona: Número de zona UTM (1-60)
        hemisferio: 'N' o 'S' para la zona UTM
        auto_zona: Si es True, detecta automáticamente la zona UTM
    """
    # Verificar existencia del archivo de entrada
    if not Path(input_path).exists():
        raise FileNotFoundError(f"❌ No se encontró el archivo: {input_path}")
    
    # Cargar datos GeoJSON
    print(f"📂 Cargando archivo: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verificar estructura básica
    if 'features' not in data:
        raise ValueError("❌ El archivo no contiene la estructura 'features' (no es GeoJSON válido)")
    
    # Detectar zona UTM si se solicita
    if auto_zona:
        primera_feature = data['features'][0]
        if primera_feature['geometry']['type'] == 'Point':
            lon = primera_feature['geometry']['coordinates'][0]
            zona = detectar_zona_utm(lon)
            print(f"🔍 Zona UTM detectada: {zona}{hemisferio}")
    
    # Configurar transformador
    epsg_code = configurar_zona_utm(zona, hemisferio)
    transformer_to_utm = Transformer.from_crs("EPSG:4326", epsg_code, always_xy=True)
    print(f"🗺️  Proyectando coordenadas a: {epsg_code}")
    
    puntos_viales = []
    errores = 0
    puntos_procesados = 0
    
    # Filtrar únicamente los puntos de control (progresivas)
    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            nombre = feature['properties'].get('name', '')
            
            # Validar que el nombre tenga formato de progresiva
            if not nombre:
                print(f"⚠️  Advertencia: Punto sin nombre en la posición {puntos_procesados + 1}")
                errores += 1
                continue
            
            lon, lat = feature['geometry']['coordinates'][:2]
            
            # Convertir el texto "K+MMM" a metros continuos (float)
            try:
                if '+' in nombre:
                    p_split = nombre.split('+')
                    km = float(p_split[0]) if p_split[0] else 0
                    m = float(p_split[1]) if len(p_split) > 1 else 0
                    distancia_m = km * 1000 + m
                else:
                    distancia_m = float(nombre.replace('+', '').strip())
            except ValueError as e:
                print(f"⚠️  Error en formato de progresiva '{nombre}': {e}")
                errores += 1
                continue
            
            # Proyectar a coordenadas planas UTM
            try:
                x, y = transformer_to_utm.transform(lon, lat)
            except Exception as e:
                print(f"⚠️  Error proyectando punto '{nombre}': {e}")
                errores += 1
                continue
            
            puntos_viales.append({
                "progresiva": nombre,
                "distancia_m": distancia_m,
                "utm_e": round(x, 3),
                "utm_n": round(y, 3),
                "lon": round(lon, 7),
                "lat": round(lat, 7)
            })
            puntos_procesados += 1
    
    if puntos_procesados == 0:
        raise ValueError("❌ No se encontraron puntos válidos en el archivo GeoJSON")
    
    # Ordenar cronológicamente por su kilometraje
    puntos_viales.sort(key=lambda p: p['distancia_m'])
    
    # Estructura final mejorada
    json_mejorado = {
        "metadata": {
            "proyecto": "Alineamiento Vial Simplificado",
            "archivo_origen": Path(input_path).name,
            "fecha_conversion": datetime.now().isoformat(),
            "sistema_referencia_plana": f"{epsg_code}",
            "sistema_referencia_geografica": "WGS 84 (EPSG:4326)",
            "zona_utm": f"{zona}{hemisferio}",
            "progresiva_inicial": puntos_viales[0]["progresiva"],
            "progresiva_final": puntos_viales[-1]["progresiva"],
            "longitud_total_m": puntos_viales[-1]["distancia_m"],
            "total_estaciones": len(puntos_viales)
        },
        "estaciones": puntos_viales
    }
    
    # Exportar el nuevo archivo JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_mejorado, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ ¡Conversión completada exitosamente!")
    print(f"   📊 Estadísticas:")
    print(f"      - Puntos procesados: {puntos_procesados}")
    print(f"      - Errores ignorados: {errores}")
    print(f"      - Longitud total: {json_mejorado['metadata']['longitud_total_m']/1000:.3f} km")
    print(f"   📁 Archivo guardado en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convierte GeoJSON de Google Earth a formato JSON estructurado para análisis vial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Conversión básica
  python convertir_geojson_a_formato.py puntos.geojson progresivas.json
  
  # Usar zona UTM específica
  python convertir_geojson_a_formato.py puntos.geojson resultado.json --zona 18 --hemisferio S
  
  # Auto-detectar zona UTM
  python convertir_geojson_a_formato.py puntos.geojson --auto
  
  # Nombre de salida automático
  python convertir_geojson_a_formato.py mi_proyecto.geojson
        """
    )
    
    parser.add_argument('input', 
                       help='Ruta del archivo GeoJSON de entrada')
    
    parser.add_argument('output', 
                       nargs='?', 
                       default=None,
                       help='Ruta del archivo JSON de salida (opcional)')
    
    parser.add_argument('--zona', 
                       type=int, 
                       default=19,
                       help='Número de zona UTM (1-60) [default: 19]')
    
    parser.add_argument('--hemisferio', 
                       choices=['N', 'S'], 
                       default='S',
                       help='Hemisferio: N (Norte) o S (Sur) [default: S]')
    
    parser.add_argument('--auto', 
                       action='store_true',
                       help='Detectar automáticamente la zona UTM')
    
    args = parser.parse_args()
    
    # Determinar nombre de salida si no se proporcionó
    if args.output is None:
        input_path = Path(args.input)
        output_path = input_path.stem + "_convertido.json"
    else:
        output_path = args.output
    
    try:
        generar_json_simplificado(
            args.input, 
            output_path, 
            args.zona, 
            args.hemisferio,
            args.auto
        )
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()