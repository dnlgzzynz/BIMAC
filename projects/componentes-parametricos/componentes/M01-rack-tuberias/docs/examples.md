# Ejemplos de Uso - M01 Rack de Tuberias

Ejemplos practicos de configuracion para diferentes aplicaciones industriales.

---

## Ejemplo 1: Rack de Proceso Tipico

Rack para planta petroquimica con multiples niveles.

### Configuracion

```yaml
geometry:
  total_length: 60000         # 60m de longitud
  bay_spacing: 6000           # Crujias de 6m
  width: 4000                 # 4m de ancho
  height: 9000                # 9m de altura
  tier_count: 4               # 4 niveles
  tier_spacing: 1200          # 1.2m entre niveles
  first_tier_height: 4500     # Primer nivel a 4.5m

structure:
  frame_type: portal_frame
  column_profile: W12x40
  beam_profile: W12x26
  strut_profile: W8x18
  bracing_profile: L4x4x3/8
  bracing_type: X
  material: A36

pipe_schedule:
  - {size: 12, count: 2, service: process, tier: 0, insulated: true}
  - {size: 10, count: 2, service: process, tier: 0, insulated: true}
  - {size: 8, count: 4, service: process, tier: 1, insulated: true}
  - {size: 6, count: 3, service: steam_low, tier: 2, insulated: true}
  - {size: 4, count: 6, service: hot_water, tier: 2, insulated: true}
  - {size: 3, count: 4, service: cold_water, tier: 3, insulated: true}
  - {size: 2, count: 8, service: gas, tier: 3, insulated: false}

supports:
  default_type: shoe
  spacing: 3000
  insulation_gap: 75

cable_tray:
  include: true
  type: ladder
  width: 600
  tier: 3

finishing: paint
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de marcos | 11 |
| Peso de estructura | 18,500 kg |
| Total de soportes | 180 |
| Longitud de tuberia | ~1,800 m |
| **Costo estimado** | **$2,850,000 MXN** |

---

## Ejemplo 2: Cruce de Vialidad

Rack elevado para cruce de camino vehicular.

### Configuracion

```yaml
geometry:
  total_length: 24000         # 24m (3 claros de 8m)
  bay_spacing: 8000           # Claros de 8m
  width: 3000                 # 3m de ancho
  height: 8000                # 8m altura total
  elevation: 0
  tier_count: 2
  tier_spacing: 1000
  first_tier_height: 6500     # Altura libre 5.5m

structure:
  frame_type: truss_frame     # Armadura para claros
  column_profile: W14x48
  beam_profile: W12x26        # Cuerda de armadura
  strut_profile: L4x4x3/8     # Alma de armadura
  bracing_profile: L5x5x1/2
  bracing_type: X
  material: A572_Gr50

pipe_schedule:
  - {size: 16, count: 1, service: oil, tier: 0, insulated: true}
  - {size: 12, count: 2, service: process, tier: 0, insulated: true}
  - {size: 8, count: 3, service: process, tier: 1, insulated: true}

supports:
  default_type: shoe
  spacing: 4000
  insulation_gap: 100

cable_tray:
  include: true
  type: ladder
  width: 450
  tier: 1

finishing: galvanize_hot
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Altura libre vehicular | 5,500 mm |
| Numero de marcos | 4 |
| Peso de estructura | 12,800 kg |
| Total de soportes | 36 |
| **Costo estimado** | **$1,650,000 MXN** |

---

## Ejemplo 3: Rack de Utilidades

Servicios de planta (agua, vapor, aire).

### Configuracion

```yaml
geometry:
  total_length: 45000         # 45m
  bay_spacing: 5000           # Claros de 5m
  width: 2500                 # 2.5m de ancho
  height: 5000                # 5m de altura
  tier_count: 2
  tier_spacing: 800
  first_tier_height: 3500

structure:
  frame_type: portal_frame
  column_profile: W10x22
  beam_profile: W8x18
  strut_profile: C8x11.5
  bracing_profile: L3x3x1/4
  bracing_type: V
  material: A36

pipe_schedule:
  - {size: 8, count: 1, service: cold_water, tier: 0, insulated: true}
  - {size: 6, count: 1, service: hot_water, tier: 0, insulated: true}
  - {size: 4, count: 2, service: steam_low, tier: 0, insulated: true}
  - {size: 3, count: 2, service: chilled, tier: 1, insulated: true}
  - {size: 2, count: 4, service: gas, tier: 1, insulated: false}
  - {size: 1, count: 8, service: gas, tier: 1, insulated: false}

supports:
  default_type: shoe
  spacing: 2500
  insulation_gap: 50

cable_tray:
  include: true
  type: ladder
  width: 300
  tier: 1

finishing: paint
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de marcos | 10 |
| Peso de estructura | 6,200 kg |
| Total de soportes | 162 |
| **Costo estimado** | **$980,000 MXN** |

---

## Ejemplo 4: Rack en Voladizo

Extension lateral desde edificio existente.

### Configuracion

```yaml
geometry:
  total_length: 30000
  bay_spacing: 5000
  width: 2000                 # Voladizo de 2m
  height: 4000
  tier_count: 2
  tier_spacing: 800
  first_tier_height: 2500

structure:
  frame_type: cantilever
  column_profile: W12x26
  beam_profile: W10x22
  strut_profile: W8x18
  bracing_profile: L4x4x3/8
  bracing_type: none          # Sin arriostramiento lateral
  material: A36

pipe_schedule:
  - {size: 6, count: 3, service: process, tier: 0, insulated: true}
  - {size: 4, count: 4, service: process, tier: 1, insulated: true}
  - {size: 2, count: 6, service: gas, tier: 1, insulated: false}

supports:
  default_type: shoe
  spacing: 2500

cable_tray:
  include: false

finishing: paint
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de marcos | 7 |
| Peso de estructura | 4,800 kg |
| Total de soportes | 78 |
| **Costo estimado** | **$720,000 MXN** |

---

## Ejemplo 5: Rack de Alta Temperatura

Para tuberias de vapor de alta presion.

### Configuracion

```yaml
geometry:
  total_length: 36000
  bay_spacing: 6000
  width: 3500
  height: 7000
  tier_count: 3
  tier_spacing: 1000
  first_tier_height: 4000

structure:
  frame_type: portal_frame
  column_profile: W14x30
  beam_profile: W12x26
  strut_profile: W8x18
  bracing_profile: L4x4x3/8
  bracing_type: X
  material: A572_Gr50

pipe_schedule:
  - {size: 10, count: 2, service: steam_high, tier: 0, insulated: true}
  - {size: 8, count: 3, service: steam_high, tier: 1, insulated: true}
  - {size: 6, count: 2, service: steam_low, tier: 2, insulated: true}
  - {size: 4, count: 4, service: hot_water, tier: 2, insulated: true}

supports:
  default_type: roller        # Rodillos para expansion termica
  spacing: 3500
  insulation_gap: 125         # Mayor gap para aislamiento grueso

cable_tray:
  include: true
  type: ladder
  width: 450
  tier: 2

finishing: fireproof          # Proteccion contra incendio
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de marcos | 7 |
| Peso de estructura | 9,400 kg |
| Expansion termica | ~180 mm |
| Total de soportes | 66 |
| Espesor aislamiento | 100-125 mm |
| **Costo estimado** | **$1,950,000 MXN** |

---

## Uso en Grasshopper

### Script Basico

```python
"""
Grasshopper Python Script
Generacion completa de pipe rack
"""

# Inputs desde componentes GH
total_length = 30000   # Number Slider
bay_spacing = 6000     # Number Slider
width = 3000           # Number Slider
height = 6000          # Number Slider
tier_count = 3         # Integer Slider
frame_type = "portal_frame"  # Value List

# Importar modulos
from rack_generator import PipeRackGenerator
from support_builder import SupportBuilder
from pipe_router import PipeRouter, PipeScheduleGenerator
from cost_calculator import PipeRackCostCalculator

# 1. Generar estructura
rack_gen = PipeRackGenerator(frame_type=frame_type)
rack_data = rack_gen.generate(
    total_length=total_length,
    bay_spacing=bay_spacing,
    width=width,
    height=height,
    tier_count=tier_count,
    column_profile='W12x26',
    beam_profile='W10x22'
)

# 2. Crear schedule de tuberias
pipe_schedule = PipeScheduleGenerator.create_process_schedule(tier_count)

# 3. Generar soportes
support_builder = SupportBuilder()
support_result = support_builder.build(
    rack_data=rack_data,
    pipe_schedule=pipe_schedule,
    support_spacing=3000,
    include_tray=True
)

# 4. Rutear tuberias
router = PipeRouter()
routing_result = router.route(
    rack_data=rack_data,
    pipe_schedule=pipe_schedule,
    include_insulation=True
)

# 5. Calcular costos
calculator = PipeRackCostCalculator()
cost_result = calculator.calculate(
    rack_data=rack_data,
    support_result=support_result,
    routing_result=routing_result
)

# Outputs para GH
columns = rack_data.columns           # Breps de columnas
beams = rack_data.beams               # Breps de vigas
bracing = rack_data.bracing           # Breps de arriostramientos
pipes = routing_result.pipes          # Breps de tuberias
insulation = routing_result.insulation
supports = support_result.shoes + support_result.guides
cable_tray = support_result.cable_tray
total_cost = cost_result.total_cost
```

### Conexiones en Canvas

```
[Number Slider: total_length] ───┐
[Number Slider: bay_spacing] ────┼──> [Python Script] ──> [Brep: columns]
[Number Slider: width] ──────────┤                    ├──> [Brep: beams]
[Number Slider: height] ─────────┤                    ├──> [Brep: bracing]
[Integer Slider: tier_count] ────┤                    ├──> [Brep: pipes]
[Value List: frame_type] ────────┘                    ├──> [Brep: insulation]
                                                      ├──> [Brep: supports]
                                                      └──> [Number: cost]
```

---

## Integracion con Revit

### Via Rhino.inside.Revit

```python
"""
Exportar a Revit como Structural Framing
"""

import clr
clr.AddReference('RhinoInside.Revit')
from RhinoInside.Revit import Revit
from Autodesk.Revit.DB import *

doc = Revit.ActiveDBDocument

with Transaction(doc, "Import Pipe Rack") as t:
    t.Start()

    # Columnas
    for i, col in enumerate(columns):
        ds = DirectShape.CreateElement(
            doc, ElementId(BuiltInCategory.OST_StructuralColumns)
        )
        ds.SetShape(col.ToRevitGeometry())
        ds.Name = f"PR-COL-{i+1:03d}"

    # Vigas
    for i, beam in enumerate(beams):
        ds = DirectShape.CreateElement(
            doc, ElementId(BuiltInCategory.OST_StructuralFraming)
        )
        ds.SetShape(beam.ToRevitGeometry())
        ds.Name = f"PR-BM-{i+1:03d}"

    # Tuberias
    for i, pipe in enumerate(pipes):
        ds = DirectShape.CreateElement(
            doc, ElementId(BuiltInCategory.OST_PipeCurves)
        )
        ds.SetShape(pipe.ToRevitGeometry())

    t.Commit()
```

---

## Comparativa de Costos

| Configuracion | Longitud | Niveles | Peso | Costo (MXN) | MXN/m |
|---------------|----------|---------|------|-------------|-------|
| Proceso tipico | 60m | 4 | 18.5 ton | $2,850,000 | $47,500 |
| Cruce vialidad | 24m | 2 | 12.8 ton | $1,650,000 | $68,750 |
| Utilidades | 45m | 2 | 6.2 ton | $980,000 | $21,778 |
| Voladizo | 30m | 2 | 4.8 ton | $720,000 | $24,000 |
| Alta temp | 36m | 3 | 9.4 ton | $1,950,000 | $54,167 |

*Precios en MXN 2024. Incluyen estructura, soportes y acabados.*

---

## Notas de Diseno

### Expansion Termica

Para servicios de alta temperatura:
- Usar soportes tipo roller o slide
- Calcular movimiento: ΔL = α × L × ΔT
- Acero: α = 12 × 10⁻⁶ /°C
- Considerar loops de expansion o juntas

### Cargas de Viento

En racks expuestos:
- Agregar arriostramiento adicional
- Verificar volteo de columnas
- Considerar factor de forma de tuberias

### Acceso y Mantenimiento

- Pasarelas cada 6-8 crujias
- Escaleras en extremos
- Espacio minimo entre tuberias: 50mm
- Altura libre sobre pasarela: 2100mm

---

*Ejemplos de uso v1.0 - M01 Rack de Tuberias Parametrico*
