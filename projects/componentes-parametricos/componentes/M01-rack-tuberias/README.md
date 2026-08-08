# M01 - Rack de Tuberias Parametrico

Componente parametrico para generacion de racks de tuberias industriales (pipe racks) con soporte para multiples niveles, configuraciones estructurales y sistemas MEP.

## Descripcion

Este componente genera estructuras de soporte para tuberias industriales, incluyendo:
- Marcos estructurales de acero
- Multiples niveles de tuberias
- Soportes y guias para tuberias
- Bandejas de cables integradas
- Conexiones y arriostramientos

## Caracteristicas

### Tipologias de Estructura

| Tipo | Descripcion | Claro Tipico | Aplicacion |
|------|-------------|--------------|------------|
| `portal_frame` | Marco portal simple | 6-12m | Plantas industriales |
| `truss_frame` | Marco con armadura | 12-24m | Claros largos |
| `cantilever` | Voladizo lateral | 3-6m | Junto a edificios |
| `elevated` | Elevado sobre columnas | 6-15m | Cruces de vialidades |
| `ground_mounted` | Montado a nivel | 3-8m | Areas de proceso |

### Configuraciones de Niveles

- **Single tier**: Un solo nivel de tuberias
- **Multi-tier**: Multiples niveles (2-6)
- **Stacked**: Niveles escalonados
- **Mixed**: Combinacion de tuberias y bandejas

### Sistemas Soportados

- Tuberias de proceso (CS, SS, alloy)
- Tuberias de servicios (agua, vapor, aire)
- Bandejas de cables (escalera, solida, malla)
- Ductos HVAC
- Instrumentacion

## Estructura del Componente

```
M01-rack-tuberias/
├── README.md
├── config.yaml
├── src/
│   └── grasshopper/
│       ├── definitions/
│       │   └── M01_PipeRack.gh
│       └── scripts/
│           ├── rack_generator.py      # Generador de estructura
│           ├── support_builder.py     # Soportes y guias
│           ├── pipe_router.py         # Ruteo de tuberias
│           ├── structural_check.py    # Validacion estructural
│           └── cost_calculator.py     # Calculadora de costos
└── docs/
    ├── parameters.md
    └── examples.md
```

## Parametros Principales

### Geometria General

| Parametro | Rango | Default | Unidad |
|-----------|-------|---------|--------|
| `total_length` | 6000-200000 | 30000 | mm |
| `bay_spacing` | 3000-12000 | 6000 | mm |
| `width` | 1500-8000 | 3000 | mm |
| `height` | 3000-15000 | 6000 | mm |
| `tier_count` | 1-6 | 3 | - |
| `tier_spacing` | 600-2000 | 1000 | mm |

### Estructura

| Parametro | Opciones | Default |
|-----------|----------|---------|
| `frame_type` | portal_frame, truss_frame, cantilever | portal_frame |
| `column_profile` | W, HSS, Pipe | W12x26 |
| `beam_profile` | W, HSS, C | W10x22 |
| `bracing_type` | none, X, V, K | X |

### Soportes de Tuberia

| Parametro | Opciones | Default |
|-----------|----------|---------|
| `support_type` | shoe, guide, anchor, hanger | shoe |
| `support_spacing` | 1500-6000 | 3000 | mm |
| `insulation_gap` | 0-150 | 50 | mm |

## Normativas Aplicables

- **AISC 360**: Diseno de acero estructural
- **ASCE 7**: Cargas de diseno
- **MSS SP-58**: Soportes de tuberia
- **MSS SP-69**: Guias y anclajes
- **NFPA 30**: Plantas de proceso
- **API 650**: Instalaciones petroleras

## Uso Rapido

```python
# Grasshopper Python
from rack_generator import PipeRackGenerator
from support_builder import SupportBuilder

# Generar estructura
rack = PipeRackGenerator()
structure = rack.generate(
    total_length=30000,
    bay_spacing=6000,
    width=3000,
    height=6000,
    tier_count=3
)

# Agregar soportes
supports = SupportBuilder()
pipe_supports = supports.build(
    structure=structure,
    pipe_schedule=[
        {'size': 6, 'count': 4},
        {'size': 4, 'count': 6},
        {'size': 2, 'count': 8}
    ]
)
```

## Integracion BIM

### Parametros Compartidos

- `BIMAC_Rack_Type`: Tipologia de rack
- `BIMAC_Rack_Length`: Longitud total
- `BIMAC_Rack_Capacity`: Capacidad de carga
- `BIMAC_Rack_Weight`: Peso estructural

### Clasificacion

- **Uniclass**: Ss_25_60_65 (Pipe support systems)
- **OmniClass**: 23-33 11 00 (Pipe Racks)
- **IFC**: IfcBuildingElementProxy / IfcMember

## Autor

- **BIMAC** - BIM Advance Consulting
- **Version**: 1.0.0
- **Fecha**: 2025-12-27
- **Estado**: En desarrollo

## Licencia

Uso interno BIMAC. Consultar terminos de licenciamiento.
