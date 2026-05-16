## 📄 README.md (para el script de conversión)

```markdown
# 🗺️ Conversor de GeoJSON a Formato Vial - Google Earth a JSON Estructurado

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![pyproj](https://img.shields.io/badge/pyproj-3.3+-green.svg)](https://pyproj4.github.io/pyproj/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Herramienta profesional para convertir puntos de control vial desde Google Earth (GeoJSON) a un formato JSON estructurado con coordenadas UTM, diseñada específicamente para ingenieros viales y topógrafos.

## 🎯 Propósito

Este script transforma archivos GeoJSON exportados desde Google Earth Pro en un formato optimizado que contiene:
- ✅ **Coordenadas UTM** (proyectadas a metros)
- ✅ **Coordenadas geográficas** (WGS84 en grados)
- ✅ **Progresivas ordenadas** automáticamente por kilometraje
- ✅ **Metadatos del proyecto** (longitud total, zona UTM, etc.)

## 📋 Requisitos Previos

### Instalación de Dependencias

```bash
pip install pyproj
```

### Archivo de Entrada Requerido

Un archivo GeoJSON válido con estructura:

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

## 🚀 Instalación

### Opción 1: Script Único (Recomendado)

1. Descarga el script `convertir_geojson_a_formato.py`
2. Guárdalo en tu carpeta de trabajo
3. Instala la dependencia:
   ```bash
   pip install pyproj
   ```

### Opción 2: Desde GitHub

```bash
git clone https://github.com/tu-usuario/conversor-vial-geojson.git
cd conversor-vial-geojson
pip install -r requirements.txt
```

## 💻 Uso del Script

### Uso Básico (Modo Consola Mejorado)

```bash
python convertir_geojson_a_formato.py input.geojson output.json
```

### Ejemplos Prácticos

```bash
# Ejemplo 1: Conversión básica
python convertir_geojson_a_formato.py puntos_viales.geojson progresivas.json

# Ejemplo 2: Auto-generar nombre de salida
python convertir_geojson_a_formato.py mi_proyecto.geojson

# Ejemplo 3: Especificar zona UTM diferente
python convertir_geojson_a_formato.py puntos.geojson resultado.json --zona 18 --hemisferio S

# Ejemplo 4: Ayuda completa
python convertir_geojson_a_formato.py --help
```

### Parámetros Disponibles

| Parámetro | Descripción | Default | Ejemplo |
|-----------|-------------|---------|---------|
| `input` | Archivo GeoJSON de entrada | **Requerido** | `puntos.geojson` |
| `output` | Archivo JSON de salida | `input_convertido.json` | `progresivas.json` |
| `--zona` | Número de zona UTM (1-60) | `19` | `--zona 18` |
| `--hemisferio` | Hemisferio (N/S) | `S` | `--hemisferio N` |
| `--auto` | Auto-detectar zona UTM | `False` | `--auto` |

## 📊 Formato de Salida

El script genera un archivo JSON con esta estructura:

```json
{
  "metadata": {
    "proyecto": "Alineamiento Vial Simplificado",
    "archivo_origen": "puntos_viales.geojson",
    "fecha_conversion": "2024-05-20T14:30:22.123456",
    "sistema_referencia_plana": "WGS 84 / UTM Zone 19S (EPSG:32719)",
    "sistema_referencia_geografica": "WGS 84 (EPSG:4326)",
    "zona_utm": "19S",
    "progresiva_inicial": "0+000",
    "progresiva_final": "15+500",
    "longitud_total_m": 15500.0,
    "total_estaciones": 32
  },
  "estaciones": [
    {
      "progresiva": "0+000",
      "distancia_m": 0.0,
      "utm_e": 123456.789,
      "utm_n": 9876543.210,
      "lon": -75.1234567,
      "lat": 4.1234567
    }
  ]
}
```
