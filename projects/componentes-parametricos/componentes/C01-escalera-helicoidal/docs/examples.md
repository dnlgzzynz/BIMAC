# Ejemplos de Uso - C01 Escalera Helicoidal

Ejemplos practicos de configuracion y uso del componente.

---

## Ejemplo 1: Escalera Residencial Compacta

Escalera de acceso interior para vivienda unifamiliar.

### Configuracion

```yaml
geometry:
  floor_to_floor: 2700      # Entrepiso tipico residencial
  outer_diameter: 1600      # Diametro compacto
  inner_diameter: 150       # Columna central
  rotation_angle: 360       # Una vuelta completa
  rotation_direction: CCW
  start_angle: 0

treads:
  riser_height: 180         # Comodo para uso residencial
  tread_thickness: 40
  nosing: 25
  material: steel
  finish: powder_coat
  open_riser: true

structure:
  type: central_column
  column_diameter: 150
  column_material: steel

railing:
  handrail_height: 950
  handrail_diameter: 42
  inner_handrail: true
  outer_handrail: true
  baluster_type: round
  baluster_spacing: 100
  infill_type: balusters

code: ntc_rcdf
use_type: residential
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de peldanos | 15 |
| Contrahuella real | 180 mm |
| Rotacion por peldano | 24° |
| Ancho libre | 725 mm |
| Huella en walkline | 218 mm |
| Peso estimado | 380 kg |
| **Costo estimado** | **$85,000 MXN** |

### Validacion Normativa

```
NTC-RCDF Residencial:
✓ Contrahuella: 180mm <= 200mm
✓ Diametro: 1600mm >= 1400mm
✓ Ancho libre: 725mm < 900mm ⚠️ (verificar uso)
✓ Altura pasamanos: 950mm (900-1070mm)
✓ Espaciamiento balaustres: 100mm <= 100mm
```

---

## Ejemplo 2: Escalera Comercial Elegante

Escalera de exhibicion para boutique o showroom.

### Configuracion

```yaml
geometry:
  floor_to_floor: 3500      # Altura comercial
  outer_diameter: 2200      # Diametro generoso
  inner_diameter: 200
  rotation_angle: 450       # 1.25 vueltas
  rotation_direction: CCW
  start_angle: 45           # Orientada a entrada

treads:
  riser_height: 175
  tread_thickness: 36       # Vidrio laminado
  nosing: 0                 # Sin nariz en vidrio
  material: glass
  finish: polish
  open_riser: true

structure:
  type: central_column
  column_diameter: 200
  column_material: steel

railing:
  handrail_height: 1000
  handrail_diameter: 42
  handrail_material: steel
  inner_handrail: true
  outer_handrail: true
  baluster_type: flat       # Solera para LED
  baluster_spacing: 100
  infill_type: glass        # Paneles de vidrio

code: ntc_rcdf
use_type: commercial
finishing: powder_coat
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de peldanos | 20 |
| Contrahuella real | 175 mm |
| Rotacion por peldano | 22.5° |
| Ancho libre | 1000 mm |
| Huella en walkline | 295 mm |
| Peso estimado | 520 kg |
| **Costo estimado** | **$285,000 MXN** |

### Notas de Diseno

- Vidrio laminado 8+8mm con canto pulido
- LED integrado en balaustres tipo flat
- Paneles de vidrio con sujecion puntual
- Acabado negro mate en estructura

---

## Ejemplo 3: Escalera Industrial OSHA

Escalera de acceso a mezzanine industrial.

### Configuracion

```yaml
geometry:
  floor_to_floor: 4000      # Altura de mezzanine
  outer_diameter: 1800
  inner_diameter: 150
  rotation_angle: 540       # 1.5 vueltas
  rotation_direction: CW    # Sentido horario
  start_angle: 0

treads:
  riser_height: 200         # Maximo OSHA
  tread_thickness: 8
  nosing: 0
  material: steel
  finish: galvanize         # Galvanizado para durabilidad
  open_riser: true

structure:
  type: double_stringer     # Doble larguero
  column_diameter: 0        # Sin columna central
  column_material: steel

railing:
  handrail_height: 900
  handrail_diameter: 42
  handrail_material: steel
  inner_handrail: true
  outer_handrail: true
  baluster_type: round
  baluster_spacing: 120     # Mayor espaciamiento industrial
  infill_type: balusters

code: osha
use_type: industrial
finishing: galvanize
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de peldanos | 20 |
| Contrahuella real | 200 mm |
| Rotacion por peldano | 27° |
| Ancho libre | 825 mm |
| Huella en walkline | 247 mm |
| Peso estimado | 680 kg |
| **Costo estimado** | **$125,000 MXN** |

### Validacion OSHA

```
OSHA Industrial:
✓ Contrahuella: 200mm <= 241mm
✓ Huella: 247mm >= 229mm
✓ Ancho libre: 825mm >= 559mm
✓ Altura pasamanos: 900mm (762-965mm)
✓ Angulo: 38° (30-50°)
```

---

## Ejemplo 4: Escalera Exterior Suspendida

Escalera de emergencia o acceso exterior.

### Configuracion

```yaml
geometry:
  floor_to_floor: 3200
  outer_diameter: 2000
  inner_diameter: 0         # Sin columna central
  rotation_angle: 360
  rotation_direction: CCW
  start_angle: 180          # Orientacion

treads:
  riser_height: 178         # Segun IBC
  tread_thickness: 8
  nosing: 25
  material: steel
  finish: galvanize
  open_riser: true          # Drenaje de agua

structure:
  type: suspended           # Suspendida
  column_diameter: 0
  column_material: steel

railing:
  handrail_height: 1070     # Maximo IBC
  handrail_diameter: 38
  handrail_material: steel
  inner_handrail: true
  outer_handrail: true
  baluster_type: round
  baluster_spacing: 100
  infill_type: mesh         # Malla para seguridad

code: ibc
use_type: commercial
finishing: galvanize
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de peldanos | 18 |
| Contrahuella real | 178 mm |
| Rotacion por peldano | 20° |
| Ancho libre | 1000 mm |
| Huella en walkline | 280 mm |
| Peso estimado | 450 kg |
| **Costo estimado** | **$165,000 MXN** |

---

## Ejemplo 5: Escalera de Madera Artesanal

Escalera residencial de alta gama en madera.

### Configuracion

```yaml
geometry:
  floor_to_floor: 2800
  outer_diameter: 1800
  inner_diameter: 200
  rotation_angle: 360
  rotation_direction: CCW
  start_angle: 0

treads:
  riser_height: 175
  tread_thickness: 45       # Madera maciza
  nosing: 30
  material: wood
  wood_species: walnut      # Nogal
  finish: lacquer
  open_riser: true

structure:
  type: double_stringer
  column_diameter: 200
  column_material: wood

railing:
  handrail_height: 950
  handrail_diameter: 50     # Perfil ovalado madera
  handrail_material: wood
  inner_handrail: true
  outer_handrail: true
  baluster_type: decorative # Torneado
  baluster_spacing: 95
  infill_type: balusters

code: ntc_rcdf
use_type: residential
finishing: lacquer
```

### Resultados Esperados

| Parametro | Valor |
|-----------|-------|
| Numero de peldanos | 16 |
| Contrahuella real | 175 mm |
| Rotacion por peldano | 22.5° |
| Ancho libre | 800 mm |
| Huella en walkline | 245 mm |
| Peso estimado | 280 kg |
| **Costo estimado** | **$320,000 MXN** |

---

## Uso en Grasshopper

### Script Basico

```python
"""
Grasshopper Python Script
Generacion de escalera helicoidal completa
"""

# Inputs desde componentes GH
floor_to_floor = 3000  # Number Slider
outer_diameter = 2000  # Number Slider
inner_diameter = 200   # Number Slider
rotation_angle = 360   # Number Slider
tread_material = "steel"  # Value List
structure_type = "central_column"  # Value List

# Importar modulos
from spiral_generator import SpiralGeometry
from tread_builder import TreadBuilder
from railing_builder import RailingBuilder
from code_validator import SpiralStairValidator
from cost_calculator import SpiralStairCostCalculator

# 1. Generar geometria espiral
spiral_gen = SpiralGeometry()
spiral_data = spiral_gen.generate(
    floor_to_floor=floor_to_floor,
    outer_diameter=outer_diameter,
    inner_diameter=inner_diameter,
    rotation_angle=rotation_angle,
    riser_height=175
)

# 2. Construir peldanos y estructura
tread_builder = TreadBuilder(
    material=tread_material,
    structure_type=structure_type
)
tread_result = tread_builder.build(
    spiral_data=spiral_data,
    tread_thickness=40,
    nosing=25,
    open_riser=True
)

# 3. Construir barandales
railing_builder = RailingBuilder(
    handrail_diameter=42,
    baluster_type='round'
)
railing_result = railing_builder.build(
    spiral_data=spiral_data,
    handrail_height=1000,
    baluster_spacing=100
)

# 4. Validar normativa
validator = SpiralStairValidator(code='ntc_rcdf', use_type='residential')
validation = validator.validate(
    spiral_data=spiral_data,
    railing_data=railing_result.summary
)

# 5. Calcular costos
calculator = SpiralStairCostCalculator()
costs = calculator.calculate(
    spiral_data=spiral_data,
    tread_result=tread_result,
    railing_data=railing_result.summary
)

# Outputs para GH
treads = tread_result.treads           # Breps de peldanos
structure = tread_result.column        # Breps de estructura
handrails = [railing_result.inner_handrail, railing_result.outer_handrail]
balusters = railing_result.balusters   # Lista de Breps
is_compliant = validation.is_compliant # Boolean
total_cost = costs.total_cost          # Number
```

### Conexiones en Canvas

```
[Number Slider: floor_to_floor] ──┐
[Number Slider: outer_diameter] ──┼──> [Python Script] ──> [Brep: treads]
[Number Slider: inner_diameter] ──┤                    ├──> [Brep: structure]
[Number Slider: rotation_angle] ──┤                    ├──> [Brep: handrails]
[Value List: tread_material] ─────┤                    ├──> [Brep: balusters]
[Value List: structure_type] ─────┘                    ├──> [Boolean: compliant]
                                                       └──> [Number: cost]
```

---

## Exportacion a Revit

### Via Rhino.inside.Revit

```python
"""
Script para exportar a Revit via RiR
"""

import clr
clr.AddReference('RhinoInside.Revit')
from RhinoInside.Revit import Revit
from Autodesk.Revit.DB import *

# Obtener documento activo
doc = Revit.ActiveDBDocument

# Crear DirectShape para cada elemento
with Transaction(doc, "Import Spiral Stair") as t:
    t.Start()

    # Importar peldanos
    for i, tread in enumerate(treads):
        ds = DirectShape.CreateElement(
            doc,
            ElementId(BuiltInCategory.OST_Stairs)
        )
        ds.SetShape(tread.ToRevitGeometry())
        ds.Name = f"Peldano_{i+1}"

    # Importar estructura
    for i, elem in enumerate(structure):
        ds = DirectShape.CreateElement(
            doc,
            ElementId(BuiltInCategory.OST_StructuralFraming)
        )
        ds.SetShape(elem.ToRevitGeometry())
        ds.Name = f"Estructura_{i+1}"

    # Importar barandales
    for i, rail in enumerate(handrails):
        if rail:
            ds = DirectShape.CreateElement(
                doc,
                ElementId(BuiltInCategory.OST_Railings)
            )
            ds.SetShape(rail.ToRevitGeometry())
            ds.Name = f"Pasamanos_{i+1}"

    t.Commit()
```

---

## Comparativa de Costos

| Configuracion | Diametro | Altura | Material | Costo Estimado |
|---------------|----------|--------|----------|----------------|
| Residencial compacta | 1600 mm | 2700 mm | Acero | $85,000 |
| Comercial elegante | 2200 mm | 3500 mm | Vidrio | $285,000 |
| Industrial OSHA | 1800 mm | 4000 mm | Acero galv. | $125,000 |
| Exterior suspendida | 2000 mm | 3200 mm | Acero galv. | $165,000 |
| Madera artesanal | 1800 mm | 2800 mm | Nogal | $320,000 |

*Precios en MXN, 2024. Incluyen materiales, fabricacion e instalacion.*

---

*Ejemplos de uso v1.0 - C01 Escalera Helicoidal Parametrica*
