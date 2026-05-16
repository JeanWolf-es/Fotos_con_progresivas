# 🛣️ Sistema de Procesamiento Vial con IA - Metadatos, IPTC y Progresivas

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange.svg)](https://mistral.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema profesional para ingenieros viales y topógrafos que automatiza el procesamiento de fotografías de carreteras, generando metadatos enriquecidos con inteligencia artificial y calculando progresivas espaciales automáticamente.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración Inicial](#-configuración-inicial)
- [Preparación de Datos Viales](#-preparación-de-datos-viales)
- [Uso del Sistema](#-uso-del-sistema)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Formato de Salida](#-formato-de-salida)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)

## ✨ Características Principales

### 🤖 Inteligencia Artificial Integrada
- **Descripción automática de imágenes** usando Mistral AI (modelo Pixtral-12B)
- **Optimización inteligente** de imágenes (300-400 KB para transmisión eficiente)
- **Análisis técnico** específico para obras viales

### 🗺️ Geoprocesamiento Avanzado
- **Cálculo automático de progresivas** basado en coordenadas GPS
- **Soporte múltiples zonas UTM** (configurable)
- **Validación espacial** con buffer de tolerancia (50m por defecto)
- **Ordenamiento cronológico** según kilometraje

### 📸 Metadatos Fotográficos
- **Extracción EXIF** completa (fecha, coordenadas GPS)
- **Escritura IPTC** estándar para compatibilidad con software profesional
- **Preservación de metadatos originales**

### 📊 Reportes y Logs
- **CSV estructurado** con todos los metadatos
- **Sistema de logs** para depuración
- **Estadísticas de procesamiento** en tiempo real

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE PROCESAMIENTO                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📸 Imágenes     →    🔍 IA Mistral    →    📝 IPTC Tags    │
│  (JPEG/RAW)           (Descripción)         (Metadatos)      │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  📍 GPS EXIF    →    🗺️ CSV Base    →    📊 Reporte Final   │
│  (Coordenadas)        (Temporal)          (Con Progresivas)  │
│                              │                                │
│                              ▼                                │
│                    🛣️ Archivo Eje Vial                        │
│                    (progresivas.json)                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Requisitos Previos

### Sistema Operativo
- Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- Python 3.8 o superior

### Hardware Recomendado
- **Mínimo**: 4GB RAM, 2GB espacio libre
- **Recomendado**: 8GB RAM, SSD, procesador multinúcleo

### Dependencias Principales
```
pandas>=1.3.0          # Manejo de datos tabulares
shapely>=1.8.0         # Geometrías espaciales
pyproj>=3.3.0          # Proyecciones cartográficas
pillow>=9.0.0          # Procesamiento de imágenes
iptcinfo3>=2.0.0       # Metadatos IPTC
requests>=2.28.0       # API de Mistral AI
```

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-vial-ia.git
cd sistema-vial-ia
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install pandas shapely pyproj pillow iptcinfo3 requests
```

### 4. Verificar Instalación

```bash
python -c "import pandas, shapely, pyproj, PIL, iptcinfo3, requests; print('✅ Todas las dependencias instaladas correctamente')"
```

## 🔑 Configuración Inicial

### Obtener API Key de Mistral AI

1. Regístrate en [Mistral AI Console](https://console.mistral.ai/)
2. Ve a "API Keys" → "Create New Key"
3. Copia la clave generada (comienza con `Kt...`)

### Configurar Credenciales

Crea el archivo `Metadatos_Mistral.json` con la siguiente estructura:

```json
{
  "MISTRAL_API_KEY": "tu_api_key_aquí"
}
```

**Ubicación recomendada**: 
- Windows: `C:\Users\TuUsuario\Downloads\CSS\comprension_word\Metadatos_Mistral.json`
- Linux/Mac: `/home/tu_usuario/.config/sistema_vial/Metadatos_Mistral.json`

### Estructura de Carpetas Recomendada

```
proyecto_vial/
│
├── scripts/
│   ├── generar_metadatos_progresivas_mistral.py
│   └── convertir_geojson_a_formato.py
│
├── datos/
│   ├── progresivas.json          # Datos del eje vial
│   ├── Metadatos_Mistral.json    # Credenciales API
│   └── metadatos_mensual.csv     # Reporte generado
│
├── fotos/
│   └── [aquí van las imágenes JPG]
│
├── logs/
│   └── error_progresivas.log
│
└── README.md
```

## 🗺️ Preparación de Datos Viales

### Paso 1: Obtener Datos desde Google Earth Pro

1. **Crear puntos de control en Google Earth Pro**:
   - Abre Google Earth Pro
   - Ve a "Añadir" → "Ruta" o "Crear carpeta"
   - Agrega puntos en cada progresiva (ej: "0+000", "0+500", "1+000")
   - Nombra cada punto con formato `K+MMM` (ej: "13+500")

2. **Exportar a KML/KMZ**:
   - Selecciona la carpeta con todos los puntos
   - "Guardar lugar como..." → Formato KML

3. **Convertir KML a JSON**:
   - Usa herramientas online o QGIS para convertir
   - O exporta directamente como GeoJSON desde Google Earth

### Paso 2: Convertir JSON a Formato Compatible

Ejecuta el script de conversión incluido:

```bash
python convertir_geojson_a_formato.py input.json output.json
```

**Formato de entrada esperado (GeoJSON)**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-75.123456, 4.123456]
      },
      "properties": {
        "name": "13+500"
      }
    }
  ]
}
```

**Formato de salida generado**:
```json
{
  "metadata": {
    "proyecto": "Alineamiento Vial Simplificado",
    "sistema_referencia_plana": "WGS 84 / UTM Zone 19S (EPSG:32719)",
    "longitud_total_m": 13500.0
  },
  "estaciones": [
    {
      "progresiva": "0+000",
      "distancia_m": 0.0,
      "utm_e": 123456.789,
      "utm_n": 987654.321,
      "lon": -75.1234567,
      "lat": 4.1234567
    }
  ]
}
```

## 🚀 Uso del Sistema

### Modo Básico (Recomendado)

```bash
python generar_metadatos_progresivas_mistral.py "C:\ruta\a\carpeta\con\fotos"
```

### Modo Interactivo

```bash
python generar_metadatos_progresivas_mistral.py
# Luego arrastra la carpeta de fotos cuando se solicite
```

### Ejemplo Completo

```bash
# 1. Preparar datos viales
python convertir_geojson_a_formato.py datos_eje_geojson.json progresivas.json

# 2. Procesar fotos
python generar_metadatos_progresivas_mistral.py "C:\proyectos\vias\fotos_mayo_2024"

# 3. Revisar resultados
# El archivo metadatos_mensual.csv se genera automáticamente
```

### Parámetros de Entrada

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `carpeta` | Ruta al directorio con imágenes JPG/JPEG | `"C:\fotos\proyecto"` |
| Parámetro general | Descripción del contexto de las fotos | `"Obras de pavimentación tramo 1"` |

## 📁 Estructura de Archivos

### Archivos de Entrada Obligatorios

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `progresivas.json` | Misma carpeta del script | Datos del eje vial con estaciones |
| `Metadatos_Mistral.json` | Ruta configurada | Credenciales API de Mistral |
| Imágenes JPG/JPEG | Carpeta especificada | Fotografías a procesar |

### Archivos de Salida Generados

| Archivo | Descripción |
|---------|-------------|
| `metadatos_mensual.csv` | Reporte completo con progresivas calculadas |
| `error_progresivas.log` | Log de errores de geoprocesamiento |

## 📊 Formato de Salida

### Estructura del CSV Final

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `Nombre` | Texto | Nombre del archivo | `IMG_20240520_143022.jpg` |
| `DIR` | Texto | Ruta absoluta | `C:\fotos\IMG_20240520_143022.jpg` |
| `FECHA` | Fecha/Hora | Fecha de captura (EXIF) | `2024:05:20 14:30:22` |
| `Latitud` | Decimal | Coordenada geográfica | `4.123456` |
| `Longitud` | Decimal | Coordenada geográfica | `-75.123456` |
| **`PROGRESIVA`** | Texto | **Kilometraje calculado** | **`13+245`** |
| `Descripción` | Texto | Análisis IA (≤150 chars) | `Pavimento deteriorado en tramo recto` |
| `Estado` | Texto | Estado del procesamiento | `OK` / `Error FASE 1` |

### Ejemplo de Salida

```csv
Nombre,FECHA,Latitud,Longitud,PROGRESIVA,Descripción,Estado
IMG_001.jpg,2024:05:20 10:30:15,4.123456,-75.123456,13+245,Pavimento con fisuras longitudinales,OK
IMG_002.jpg,2024:05:20 10:32:20,4.123789,-75.124567,13+378,Señalización vertical presente,OK
```

## 🔍 Solución de Problemas

### Error: "No se encontró el archivo de credenciales"

**Solución**: Verifica la ruta del archivo `Metadatos_Mistral.json`:

```python
# Modifica esta línea en el script si es necesario
CREDENTIALS_PATH = r"tu_ruta_personalizada\Metadatos_Mistral.json"
```

### Error: "No se encontró el archivo geométrico del eje"

**Solución**: Asegúrate de que `progresivas.json` esté en la misma carpeta que el script.

### Error: "Puntos fuera de rango (>50m)"

**Posibles causas**:
- Coordenadas GPS inexactas en las fotos
- Eje vial mal definido
- Zona UTM incorrecta

**Soluciones**:
1. Verifica la precisión GPS de tus fotos
2. Ajusta `BUFFER_TOLERANCIA_M` en el script (línea 25)
3. Revisa el log `error_progresivas.log`

### Error de Zona UTM

Si trabajas en zona UTM diferente a 19S, modifica:

```python
# Línea 175 del script principal
return pyproj.Transformer.from_crs("EPSG:4326", "EPSG:327XX", always_xy=True)
# Reemplaza XX con tu zona (ej: 17N = 32617)
```

### Problemas con IPTC en Linux/Mac

```bash
# Instalar dependencias adicionales
sudo apt-get update
sudo apt-get install libimage-exiftool-perl  # Linux
# o
brew install exiftool  # Mac
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. **Crea una rama** (`git checkout -b feature/mejora`)
3. **Commit** tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/mejora`)
5. Abre un **Pull Request**

### Áreas de Mejora Identificadas

- [ ] Soporte para zonas UTM automático
- [ ] Procesamiento batch con paralelización
- [ ] Interfaz gráfica simple (GUI)
- [ ] Exportación a formatos GIS (Shapefile, GeoPackage)
- [ ] Validación automática de calidad de fotos
- [ ] Generación de reportes PDF con mapas

## 📄 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para reportar bugs o solicitar features:
- Abrir **Issue** en GitHub
- Contacto directo: [tu-email@dominio.com]
- Documentación adicional: [Wiki del proyecto]

---

## 🏆 Créditos

Desarrollado por [Tu Nombre] para la ingeniería vial y topografía de precisión.

**¡Optimiza tu flujo de trabajo vial con inteligencia artificial!** 🚀
```

## Script de Conversión (adaptado para consola)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
convertir_geojson_a_formato.py
Convierte archivos GeoJSON exportados desde Google Earth al formato requerido
por el Sistema de Procesamiento Vial con IA.

Uso:
    python convertir_geojson_a_formato.py input.geojson output.json
    python convertir_geojson_a_formato.py --input progresivas.geojson --output progresivas_viales.json
"""

import json
import argparse
import sys
from pathlib import Path
from pyproj import Transformer


def configurar_zona_utm(zona=None, hemisferio='S'):
    """
    Configura la zona UTM para la proyección.
    
    Args:
        zona: Número de zona UTM (1-60). Si es None, intenta detectar automáticamente.
        hemisferio: 'N' para norte, 'S' para sur
    
    Returns:
        str: Código EPSG para la zona UTM configurada
    """
    if zona is None:
        # Por defecto, zona 19 para Colombia y Centroamérica
        zona = 19
    
    hemisferio_codigo = 6 if hemisferio == 'N' else 7
    epsg = int(f"326{hemisferio_codigo}{zona:02d}") if zona < 10 else int(f"32{hemisferio_codigo}{zona}")
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


def generar_json_simplificado(input_path, output_path, zona_utm=None, hemisferio='S'):
    """
    Convierte un GeoJSON de Google Earth al formato requerido por el script principal.
    
    Args:
        input_path: Ruta del archivo GeoJSON de entrada
        output_path: Ruta del archivo JSON de salida
        zona_utm: Número de zona UTM (opcional, auto-detectar si None)
        hemisferio: 'N' o 'S' para la zona UTM
    """
    # Verificar existencia del archivo de entrada
    if not Path(input_path).exists():
        raise FileNotFoundError(f"No se encontró el archivo: {input_path}")
    
    # Cargar datos GeoJSON
    print(f"📂 Cargando archivo: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verificar estructura básica
    if 'features' not in data:
        raise ValueError("El archivo no contiene la estructura 'features' esperada (no es GeoJSON válido)")
    
    # Detectar zona UTM si no se especificó
    if zona_utm is None:
        # Tomar primera coordenada como referencia
        primera_feature = data['features'][0]
        if primera_feature['geometry']['type'] == 'Point':
            lon = primera_feature['geometry']['coordinates'][0]
            zona_utm = detectar_zona_utm(lon)
            print(f"🔍 Zona UTM detectada: {zona_utm}{hemisferio}")
    
    # Configurar transformador
    epsg_code = configurar_zona_utm(zona_utm, hemisferio)
    transformer_to_utm = Transformer.from_crs("EPSG:4326", epsg_code, always_xy=True)
    print(f"🗺️  Proyectando a: {epsg_code}")
    
    puntos_viales = []
    errores = 0
    puntos_procesados = 0
    
    # Filtrar únicamente los puntos de control (progresivas)
    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            nombre = feature['properties'].get('name', '')
            
            # Validar que el nombre tenga formato de progresiva
            if not nombre or ('+' not in nombre and not nombre.replace('+', '').isdigit()):
                print(f"⚠️  Advertencia: El punto '{nombre}' no tiene formato de progresiva válido")
                errores += 1
                continue
            
            lon, lat = feature['geometry']['coordinates'][:2]
            
            # Convertir el texto "K+MMM" a metros continuos (float)
            try:
                if '+' in nombre:
                    partes = nombre.split('+')
                    km = float(partes[0]) if partes[0] else 0
                    m = float(partes[1]) if len(partes) > 1 else 0
                    distancia_m = km * 1000 + m
                else:
                    # Asumir que es un número en metros
                    distancia_m = float(nombre)
            except ValueError as e:
                print(f"❌ Error parsing progresiva '{nombre}': {e}")
                errores += 1
                continue
            
            # Proyectar a coordenadas planas UTM
            try:
                x, y = transformer_to_utm.transform(lon, lat)
            except Exception as e:
                print(f"❌ Error proyectando punto '{nombre}': {e}")
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
        raise ValueError("No se encontraron puntos válidos en el archivo GeoJSON")
    
    # Ordenar cronológicamente por su kilometraje
    puntos_viales.sort(key=lambda p: p['distancia_m'])
    
    # Estructura final mejorada
    json_mejorado = {
        "metadata": {
            "proyecto": "Alineamiento Vial Simplificado",
            "archivo_origen": Path(input_path).name,
            "fecha_conversion": __import__('datetime').datetime.now().isoformat(),
            "sistema_referencia_plana": f"{epsg_code}",
            "sistema_referencia_geografica": "WGS 84 (EPSG:4326)",
            "zona_utm": f"{zona_utm}{hemisferio}",
            "progresiva_inicial": puntos_viales[0]["progresiva"],
            "progresiva_final": puntos_viales[-1]["progresiva"],
            "longitud_total_m": puntos_viales[-1]["distancia_m"],
            "total_estaciones": len(puntos_viales)
        },
        "estaciones": puntos_viales
    }
    
    # Exportar el nuevo archivo JSON plano
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_mejorado, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Conversión completada exitosamente!")
    print(f"   📊 Estadísticas:")
    print(f"      - Puntos procesados: {puntos_procesados}")
    print(f"      - Errores ignorados: {errores}")
    print(f"      - Longitud total: {json_mejorado['metadata']['longitud_total_m']/1000:.3f} km")
    print(f"   📁 Archivo guardado en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convierte GeoJSON de Google Earth al formato requerido por el Sistema de Procesamiento Vial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Uso básico
  python convertir_geojson_a_formato.py puntos_viales.geojson progresivas.json
  
  # Especificando zona UTM manualmente
  python convertir_geojson_a_formato.py puntos.geojson output.json --zona 18 --hemisferio S
  
  # Auto-detectar zona (basado en primera coordenada)
  python convertir_geojson_a_formato.py puntos.geojson output.json --auto
        """
    )
    
    parser.add_argument('input', help='Ruta del archivo GeoJSON de entrada')
    parser.add_argument('output', nargs='?', default=None, 
                       help='Ruta del archivo JSON de salida (opcional)')
    parser.add_argument('--zona', type=int, help='Número de zona UTM (1-60)')
    parser.add_argument('--hemisferio', choices=['N', 'S'], default='S',
                       help='Hemisferio: N (Norte) o S (Sur) [default: S]')
    parser.add_argument('--auto', action='store_true',
                       help='Detectar automáticamente la zona UTM')
    
    args = parser.parse_args()
    
    # Determinar nombre de salida si no se proporcionó
    if args.output is None:
        input_path = Path(args.input)
        output_path = input_path.stem + "_convertido.json"
        args.output = output_path
    
    zona_utm = None if args.auto else args.zona
    
    try:
        generar_json_simplificado(args.input, args.output, zona_utm, args.hemisferio)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Instrucciones de Uso para el Script de Conversión

### Guardar el Script

Guarda el código anterior como `convertir_geojson_a_formato.py` en la misma carpeta que tu script principal.

### Uso desde Línea de Comandos

```bash
# Conversión básica (auto-detecta zona UTM)
python convertir_geojson_a_formato.py progresivas.geojson

# Especificando zona UTM manualmente (recomendado)
python convertir_geojson_a_formato.py progresivas.geojson progresivas.json --zona 19 --hemisferio S

# Ver ayuda completa
python convertir_geojson_a_formato.py --help
```

### Integración con el Script Principal

1. **Prepara tus datos** en Google Earth Pro
2. **Exporta a KML/KMZ** y conviértelo a GeoJSON (puedes usar [mapshaper.org](https://mapshaper.org) o QGIS)
3. **Ejecuta la conversión**:
   ```bash
   python convertir_geojson_a_formato.py mi_proyecto.geojson progresivas.json --zona 19 --hemisferio S
   ```
4. **Ejecuta el procesamiento principal**:
   ```bash
   python generar_metadatos_progresivas_mistral.py "C:\ruta\fotos"
