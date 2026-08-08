# C01 - Escalera Helicoidal Parametrica

Sistema completo para generacion de escaleras helicoidales y de caracol con validacion normativa, estructura central o perimetral, y barandales integrados.

---

## Caracteristicas

- **Geometria precisa**: Espiral logaritmica con control de parametros
- **Multiples tipologias**: Central column, cantilever, perimetral, doble helice
- **Validacion normativa**: Cumplimiento automatico de codigos de construccion
- **Materiales diversos**: Acero, concreto, madera, vidrio, combinados
- **Barandales integrados**: Balaustres, paneles de vidrio, cables
- **Integracion BIM**: Exportacion directa a Revit

---

## Tipologias Soportadas

### Por Estructura

| Tipo | Descripcion | Diametro Min | Uso Tipico |
|------|-------------|--------------|------------|
| **central_column** | Columna central de soporte | 1400 mm | Residencial, comercial |
| **cantilever** | Peldanos empotrados en muro | 1600 mm | Espacios reducidos |
| **perimeter_beam** | Viga helicoidal perimetral | 1800 mm | Arquitectonico |
| **double_helix** | Dos escaleras entrelazadas | 2400 mm | Monumental |
| **suspended** | Colgada de estructura superior | 1600 mm | Contemporaneo |

### Por Material

| Material | Estructura | Peldanos | Barandal |
|----------|------------|----------|----------|
| **Acero** | Tubo/Perfil | Lamina + antiderrapante | Tubo/Solera |
| **Concreto** | Armado in situ | Concreto pulido | Acero/Vidrio |
| **Madera** | Poste central | Madera maciza | Madera/Cable |
| **Mixto** | Acero | Madera/Vidrio | Acero/Vidrio |

---

## Parametros Principales

### Geometria

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `floor_to_floor` | float | 2400-6000 | 3000 | mm | Altura entre pisos |
| `outer_diameter` | float | 1400-4000 | 2000 | mm | Diametro exterior |
| `inner_diameter` | float | 100-1000 | 200 | mm | Diametro columna central |
| `rotation_angle` | float | 270-720 | 360 | grados | Giro total |
| `rotation_direction` | enum | CW, CCW | CCW | - | Sentido de giro |
| `landing_angle` | float | 0-90 | 0 | grados | Angulo de descanso |

### Peldanos

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `riser_height` | float | 150-200 | 180 | mm | Altura de contrahuella |
| `tread_depth_inner` | float | 150-300 | 200 | mm | Huella en borde interior |
| `tread_depth_outer` | float | 250-400 | 300 | mm | Huella en borde exterior |
| `tread_thickness` | float | 20-80 | 40 | mm | Espesor del peldano |
| `nosing` | float | 0-40 | 25 | mm | Proyeccion de nariz |
| `tread_material` | enum | steel, wood, glass, concrete | steel | - | Material |

### Barandal

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `handrail_height` | float | 900-1100 | 1000 | mm | Altura de pasamanos |
| `handrail_diameter` | float | 35-50 | 42 | mm | Diametro pasamanos |
| `baluster_spacing` | float | 100-150 | 120 | mm | Espaciado de balaustres |
| `baluster_type` | enum | round, square, panel | round | - | Tipo de balaustre |
| `inner_handrail` | bool | true/false | true | - | Pasamanos interior |
| `outer_handrail` | bool | true/false | true | - | Pasamanos exterior |

---

## Estructura de Archivos

```
C01-escalera-helicoidal/
├── config.yaml                    # Configuracion
├── README.md                      # Documentacion
├── src/
│   ├── grasshopper/
│   │   ├── C01_EscaleraHelicoidal.gh   # Definicion principal
│   │   └── scripts/
│   │       ├── spiral_generator.py     # Generador de espiral
│   │       ├── tread_builder.py        # Constructor de peldanos
│   │       ├── structure_builder.py    # Estructura de soporte
│   │       ├── railing_builder.py      # Barandales
│   │       ├── code_validator.py       # Validacion normativa
│   │       └── cost_calculator.py      # Calculadora de costos
│   └── revit/
│       ├── families/
│       │   ├── BIMAC_Spiral_Tread.rfa
│       │   ├── BIMAC_Spiral_Column.rfa
│       │   └── BIMAC_Spiral_Railing.rfa
│       └── scripts/
│           └── export_stair.py
├── docs/
│   ├── parameters.md
│   ├── examples.md
│   └── codes.md
└── exports/
```

---

## Normativas Aplicables

### Mexico (NTC-RCDF)

| Parametro | Residencial | Comercial | Industrial |
|-----------|-------------|-----------|------------|
| Huella minima | 250 mm | 280 mm | 250 mm |
| Peralte maximo | 200 mm | 180 mm | 200 mm |
| Ancho minimo | 900 mm | 1200 mm | 900 mm |
| Altura pasamanos | 900 mm | 900 mm | 1070 mm |
| Espaciado balaustres | 100 mm | 100 mm | 100 mm |

### Internacional (IBC)

| Parametro | Valor |
|-----------|-------|
| Huella minima en linea de paso | 280 mm (11") |
| Peralte maximo | 190 mm (7.5") |
| Radio minimo linea de paso | 760 mm desde eje |
| Altura minima libre | 2030 mm (80") |

---

## Uso Rapido

### Grasshopper

1. Especificar `floor_to_floor` y `outer_diameter`
2. El sistema calcula automaticamente numero de peldanos
3. Ajustar parametros de barandal
4. Verificar cumplimiento normativo

### Python

```python
from C01_escalera import SpiralStairGenerator

generator = SpiralStairGenerator()

config = {
    "floor_to_floor": 3000,
    "outer_diameter": 2000,
    "inner_diameter": 200,
    "rotation_angle": 360,
    "riser_height": 175,
    "tread_material": "steel",
    "handrail_height": 1000
}

result = generator.generate(config)

print(f"Peldanos: {result.tread_count}")
print(f"Cumple normativa: {result.code_compliance}")
```

---

## Costos Estimados

### Acero (MXN por escalera completa)

| Diametro | Altura 3m | Altura 4m | Altura 5m |
|----------|-----------|-----------|-----------|
| 1.5m | $85,000 | $110,000 | $140,000 |
| 2.0m | $110,000 | $145,000 | $185,000 |
| 2.5m | $145,000 | $190,000 | $240,000 |

*Incluye: estructura, peldanos, barandal, pintura. No incluye instalacion.*

---

*Componente C01 - BIMAC Componentes Parametricos v1.0*
