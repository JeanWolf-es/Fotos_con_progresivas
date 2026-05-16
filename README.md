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
- Contacto directo: [nesnae@gmail.com]

---

## 🏆 Créditos

Desarrollado por [Jean Wolf] para la ingeniería vial y topografía de precisión.

