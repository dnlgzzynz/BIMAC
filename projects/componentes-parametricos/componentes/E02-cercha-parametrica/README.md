# E02 - Cercha Parametrica

Sistema completo para generacion de cerchas y armaduras estructurales con multiples tipologias, optimizacion de peso y conexiones detalladas.

---

## Caracteristicas

- **Multiples tipologias**: Warren, Pratt, Howe, Fink, Scissors, Bowstring, etc.
- **Geometria adaptativa**: Cerchas rectas, curvas y de pendiente variable
- **Optimizacion estructural**: Dimensionamiento automatico de perfiles
- **Conexiones detalladas**: Nodos soldados, atornillados o articulados
- **Integracion BIM**: Exportacion a Revit con familias estructurales

---

## Tipologias Soportadas

### Cerchas Triangulares (Cubiertas)

| Tipo | Descripcion | Luz Tipica | Uso |
|------|-------------|------------|-----|
| **Fink** | Diagonales en W | 6-12m | Residencial, naves pequenas |
| **Howe** | Verticales + diagonales hacia afuera | 8-20m | Naves industriales |
| **Pratt** | Verticales + diagonales hacia centro | 8-25m | Puentes, cubiertas |
| **Warren** | Solo diagonales alternadas | 10-40m | Puentes, cubiertas grandes |
| **Scissors** | Cuerdas cruzadas | 8-15m | Techos con altura interior |
| **Fan** | Diagonales radiales desde apoyo | 6-15m | Auditorios |

### Cerchas Paralelas (Vigas)

| Tipo | Descripcion | Luz Tipica | Uso |
|------|-------------|------------|-----|
| **Parallel Pratt** | Cuerdas paralelas, diagonales al centro | 15-50m | Puentes, naves |
| **Parallel Warren** | Cuerdas paralelas, diagonales alternas | 20-60m | Grandes luces |
| **Vierendeel** | Sin diagonales (marcos rigidos) | 8-20m | Arquitectonico |
| **K-Truss** | Diagonales en K | 30-100m | Puentes largos |

### Cerchas Curvas

| Tipo | Descripcion | Luz Tipica | Uso |
|------|-------------|------------|-----|
| **Bowstring** | Cuerda superior curva | 20-60m | Hangares, estadios |
| **Crescent** | Ambas cuerdas curvas | 15-40m | Cubiertas organicas |
| **Lenticular** | Forma de lente | 30-80m | Puentes |
| **Parabolic** | Cuerda parabolica | 25-70m | Cubiertas tensionadas |

---

## Parametros Principales

### Geometria

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `span` | float | 3000-100000 | 12000 | Luz libre (mm) |
| `height` | float | span/4-span/8 | auto | Altura en centro (mm) |
| `slope` | float | 0-45 | 15 | Pendiente (grados) |
| `bay_count` | int | 4-30 | 8 | Numero de modulos |
| `truss_type` | enum | ver tipologias | pratt | Tipo de cercha |

### Perfiles

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `top_chord_profile` | str | HSS, W, C, L, Pipe | HSS | Perfil cuerda superior |
| `bottom_chord_profile` | str | HSS, W, C, L, Pipe | HSS | Perfil cuerda inferior |
| `web_profile` | str | HSS, L, Pipe, Rod | HSS | Perfil de alma |
| `material` | enum | A36, A572-50, A500 | A500 | Material de acero |

### Conexiones

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `connection_type` | enum | welded, bolted, pinned | welded | Tipo de conexion |
| `gusset_plate` | bool | true/false | true | Usar placas de nodo |
| `gusset_thickness` | float | 6-25 | 12 | Espesor placa (mm) |

---

## Estructura de Archivos

```
E02-cercha-parametrica/
├── config.yaml                  # Configuracion del componente
├── README.md                    # Esta documentacion
├── src/
│   ├── grasshopper/
│   │   ├── E02_CerchaParametrica.gh   # Definicion principal
│   │   └── scripts/
│   │       ├── truss_generator.py     # Generador de geometria
│   │       ├── profile_selector.py    # Selector de perfiles
│   │       ├── node_builder.py        # Constructor de nodos
│   │       ├── structural_analysis.py # Analisis estructural
│   │       └── cost_calculator.py     # Calculadora de costos
│   └── revit/
│       ├── families/
│       │   ├── BIMAC_Truss_Chord.rfa
│       │   ├── BIMAC_Truss_Web.rfa
│       │   └── BIMAC_Truss_Node.rfa
│       └── scripts/
│           └── export_truss.py
├── docs/
│   ├── parameters.md
│   ├── examples.md
│   └── structural_notes.md
└── exports/
```

---

## Uso Rapido

### Grasshopper

1. Conectar linea base o curva al input `Base Curve`
2. Seleccionar tipologia en dropdown `Truss Type`
3. Ajustar `Span`, `Height`, `Bay Count`
4. El sistema genera automaticamente la cercha

### Python

```python
from E02_cercha import TrussGenerator

generator = TrussGenerator()

config = {
    "span": 18000,           # 18m de luz
    "height": 2500,          # 2.5m de altura
    "slope": 10,             # 10 grados
    "bay_count": 10,         # 10 modulos
    "truss_type": "warren",
    "top_chord": "HSS_150x150x6",
    "bottom_chord": "HSS_150x150x6",
    "web_members": "HSS_100x100x4"
}

result = generator.generate(config)

print(f"Peso total: {result.total_weight:.0f} kg")
print(f"Miembros: {len(result.members)}")
```

---

## Normativas

- **AISC 360-22**: Specification for Structural Steel Buildings
- **NTC-DCEA 2017**: Normas Tecnicas Complementarias para Diseno de Estructuras de Acero (CDMX)
- **AWS D1.1**: Structural Welding Code
- **ASTM A500**: Cold-Formed Welded Steel Tubing

---

## Costos Estimados

| Componente | Costo Unitario | Notas |
|------------|----------------|-------|
| Acero estructural | $28-35 MXN/kg | Incluye material |
| Fabricacion | $18-25 MXN/kg | Corte, soldadura |
| Galvanizado | $8-12 MXN/kg | Inmersion en caliente |
| Pintura | $120-180 MXN/m2 | Esmalte alquidalico |
| Montaje | $12-18 MXN/kg | Con grua |

---

*Componente E02 - BIMAC Componentes Parametricos v1.0*
