# F01 - Muro Cortina Parametrico

Sistema de muro cortina completamente parametrico con mullions variables, paneles mixtos (vidrio/solido), y capacidad de adaptacion a superficies curvas.

---

## Caracteristicas

- **Grilla adaptativa**: Se ajusta a cualquier superficie (plana, cilindrica, conica, NURBS)
- **Mullions variables**: Perfiles de aluminio con dimensiones parametricas
- **Paneles mixtos**: Combinacion de vidrio, spandrel, y paneles solidos
- **Orientacion inteligente**: Optimizacion de paneles segun orientacion solar
- **Integracion BIM**: Exportacion directa a Revit con familias adaptativas

---

## Parametros Principales

### Geometria Base

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `surface` | Surface | - | - | Superficie base del muro cortina |
| `u_divisions` | int | 1-100 | 10 | Divisiones horizontales |
| `v_divisions` | int | 1-50 | 5 | Divisiones verticales |
| `module_width` | float | 600-3000 | 1500 | Ancho de modulo (mm) |
| `module_height` | float | 1000-4500 | 3600 | Alto de modulo (mm) |

### Mullions

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `mullion_width` | float | 40-150 | 65 | Ancho del perfil (mm) |
| `mullion_depth` | float | 50-250 | 150 | Profundidad del perfil (mm) |
| `mullion_type` | enum | standard/thermal/structural | standard | Tipo de perfil |
| `transom_width` | float | 40-150 | 50 | Ancho del travesano (mm) |
| `transom_depth` | float | 50-200 | 120 | Profundidad del travesano (mm) |

### Paneles

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `glass_type` | enum | single/double/triple | double | Tipo de vidrio |
| `glass_thickness` | float | 6-44 | 24 | Espesor total (mm) |
| `spandrel_height` | float | 0-1200 | 900 | Altura del spandrel (mm) |
| `panel_pattern` | enum | vision/mixed/alternating | mixed | Patron de paneles |
| `vision_percent` | float | 30-100 | 70 | Porcentaje de vision (%) |

### Estructural

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `max_span` | float | 3000-6000 | 4500 | Luz maxima sin soporte (mm) |
| `wind_load` | float | 0.5-3.0 | 1.2 | Carga de viento (kPa) |
| `seismic_zone` | enum | A/B/C/D | C | Zona sismica |
| `anchor_spacing` | float | 1000-3000 | 1800 | Espaciado de anclajes (mm) |

---

## Estructura de Archivos

```
F01-muro-cortina/
├── config.yaml              # Configuracion del componente
├── README.md                # Esta documentacion
├── src/
│   ├── grasshopper/
│   │   ├── F01_MuroCortina.gh           # Definicion principal
│   │   └── scripts/
│   │       ├── grid_generator.py         # Generador de grilla
│   │       ├── mullion_builder.py        # Constructor de mullions
│   │       ├── panel_classifier.py       # Clasificador de paneles
│   │       ├── structural_check.py       # Validacion estructural
│   │       └── cost_calculator.py        # Calculadora de costos
│   └── revit/
│       ├── families/
│       │   ├── BIMAC_CW_Mullion.rfa      # Familia de mullion
│       │   ├── BIMAC_CW_Transom.rfa      # Familia de travesano
│       │   └── BIMAC_CW_Panel.rfa        # Familia de panel
│       └── scripts/
│           └── export_curtainwall.py     # Exportador RiR
├── docs/
│   ├── parameters.md        # Tabla completa de parametros
│   ├── examples.md          # Casos de uso
│   └── specifications.md    # Especificaciones tecnicas
└── exports/
    ├── ifc/
    ├── excel/
    └── images/
```

---

## Uso Rapido

### En Grasshopper

1. Abrir `F01_MuroCortina.gh`
2. Conectar superficie base al input `Surface`
3. Ajustar parametros en el panel de control
4. Ejecutar generacion

### Codigo Python

```python
from componentes.F01_muro_cortina import CurtainWallGenerator

# Crear generador
generator = CurtainWallGenerator()

# Configurar
config = {
    "u_divisions": 12,
    "v_divisions": 4,
    "mullion_width": 65,
    "mullion_depth": 150,
    "glass_type": "double",
    "panel_pattern": "mixed"
}

# Generar
result = generator.generate(surface, config)

# Acceder a componentes
mullions = result.mullions
transoms = result.transoms
panels = result.panels
anchors = result.anchors
```

---

## Tipos de Muro Cortina Soportados

### 1. Stick System (Palo y Travesano)
- Mullions y travesanos ensamblados en sitio
- Maxima flexibilidad geometrica
- Ideal para superficies curvas

### 2. Unitized System (Modular)
- Paneles prefabricados en fabrica
- Instalacion rapida
- Mejor control de calidad

### 3. Structural Glazing
- Vidrio fijo con silicona estructural
- Apariencia flush (sin marco visible)
- Mayor exposicion del vidrio

### 4. Point-Fixed (Spider)
- Vidrio soportado por rotulas
- Maxima transparencia
- Requiere estructura secundaria

---

## Normativas Consideradas

- **NMX-R-060-SCFI-2013**: Muros cortina - Resistencia estructural
- **ASTM E330**: Prueba de carga de viento
- **ASTM E331**: Infiltracion de agua
- **AAMA 501**: Metodos de prueba para muros cortina
- **EN 13830**: Norma europea de muros cortina

---

## Costos Estimados (MXN/m2)

| Sistema | Basico | Estandar | Premium |
|---------|--------|----------|---------|
| Stick System | 3,500 | 5,200 | 7,800 |
| Unitized | 5,500 | 7,500 | 11,000 |
| Structural Glazing | 6,200 | 8,500 | 13,500 |
| Point-Fixed | 8,000 | 12,000 | 18,000 |

*Precios incluyen: aluminio, vidrio, selladores, herrajes. No incluyen: estructura de soporte, instalacion.*

---

## Proximos Pasos

1. [x] Estructura de carpetas
2. [ ] Libreria core de geometria
3. [ ] Scripts de generacion de mullions
4. [ ] Sistema de paneles mixtos
5. [ ] Validadores y calculadora de costos
6. [ ] Documentacion completa

---

*Componente F01 - BIMAC Componentes Parametricos v1.0*
