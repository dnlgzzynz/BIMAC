# Ejemplos de Uso - E02 Cercha Parametrica

Casos de uso practicos para diferentes aplicaciones.

---

## Ejemplo 1: Nave Industrial Basica

### Descripcion
Cercha Pratt para nave industrial de 18m de luz.

### Configuracion

```yaml
geometry:
  span: 18000           # 18m
  height: 2200          # 2.2m (ratio 1:8)
  slope: 10             # 10 grados
  bay_count: 10
  truss_type: "pratt"

profiles:
  top_chord: "HSS_150x150x6"
  bottom_chord: "HSS_150x150x6"
  web_diagonal: "HSS_100x100x4"
  web_vertical: "HSS_75x75x3"
  material: "A500_Gr_B"

connections:
  type: "welded"
  gusset_thickness: 12
  weld_size: 6

loads:
  dead: 0.5             # kN/m (cubierta lamina)
  live: 0.4             # kN/m (mantenimiento)

finishing: "paint"
```

### Codigo Python

```python
from E02_cercha import TrussGenerator, ProfileSelector, TrussCostCalculator

# Generar geometria
generator = TrussGenerator()
truss = generator.generate(
    span=18000,
    height=2200,
    slope=10,
    bay_count=10,
    truss_type='pratt'
)

# Seleccionar perfiles
selector = ProfileSelector(material='A500_Gr_B')
profiles = selector.select_profiles(
    truss.member_data,
    profile_type='HSS'
)

# Calcular peso
total_weight = selector.calculate_total_weight(profiles)
print(f"Peso total: {total_weight:.0f} kg")

# Calcular costos
calculator = TrussCostCalculator()
cost = calculator.calculate(
    truss.member_data,
    profiles,
    None,
    truss.geometry_stats,
    finishing='paint'
)

print(f"Costo total: ${cost.total_cost:,.0f} MXN")
print(f"Costo/kg: ${cost.cost_per_kg:.2f} MXN/kg")
```

### Resultados Tipicos

| Metrica | Valor |
|---------|-------|
| Peso total | 850 kg |
| Costo total | $95,000 MXN |
| Costo/kg | $112 MXN/kg |
| Costo/m de luz | $5,280 MXN/m |

---

## Ejemplo 2: Cubierta de Estadio (Bowstring)

### Descripcion
Cercha bowstring para graderia de estadio, 45m de luz.

### Configuracion

```yaml
geometry:
  span: 45000           # 45m
  height: 5400          # ratio 1:8.3
  slope: 0
  bay_count: 18
  truss_type: "bowstring"

profiles:
  top_chord: "HSS_250x250x10"
  bottom_chord: "HSS_200x200x10"
  web_diagonal: "HSS_150x150x6"
  web_vertical: "HSS_100x100x5"
  material: "A572_Gr50"

connections:
  type: "bolted"
  gusset_thickness: 20
  bolt_diameter: 24
  bolt_grade: "A325"

loads:
  dead: 1.2             # Cubierta + instalaciones
  live: 0.5
  wind: 1.5             # Carga de viento critica

finishing: "galvanize"
```

### Consideraciones Especiales

1. **Cuerda curva**: La cuerda superior sigue un arco parabolico
2. **Prefabricacion**: Dividir en secciones transportables (<12m)
3. **Conexiones de campo**: Usar conexiones atornilladas
4. **Contraflecha**: Aplicar contraflecha de L/300

### Codigo

```python
# Generar cercha bowstring
truss = generator.generate(
    span=45000,
    height=5400,
    bay_count=18,
    truss_type='bowstring'
)

# Verificar curvatura
for node in truss.nodes:
    print(f"Nodo {node.id}: Z = {node.point.Z:.0f} mm")

# Secciones de transporte
max_section = 12000  # 12m
n_sections = math.ceil(45000 / max_section)
print(f"Dividir en {n_sections} secciones")
```

---

## Ejemplo 3: Puente Peatonal (Warren Paralela)

### Descripcion
Cercha Warren paralela para puente peatonal de 25m.

### Configuracion

```yaml
geometry:
  span: 25000
  height: 1800          # Peralte 1:14
  slope: 0
  bay_count: 12
  truss_type: "parallel_warren"

profiles:
  top_chord: "HSS_175x175x8"
  bottom_chord: "HSS_175x175x8"
  web_diagonal: "HSS_125x125x5"
  material: "A500_Gr_C"

connections:
  type: "welded"
  gusset_thickness: 16

loads:
  dead: 0.8
  live: 5.0             # 5 kN/m2 peatonal
  wind: 0.8

supports:
  left: "fixed"
  right: "roller"

finishing: "galvanize"
```

### Verificaciones Adicionales

```python
# Verificar deflexion para peatones
max_deflection = span / 500  # Limite para confort
print(f"Deflexion maxima permitida: {max_deflection:.0f} mm")

# Verificar frecuencia natural (vibracion)
# f > 3 Hz para evitar resonancia con paso
```

---

## Ejemplo 4: Techo de Auditorio (Scissors)

### Descripcion
Cercha tipo scissors para maximizar altura interior.

### Configuracion

```yaml
geometry:
  span: 15000
  height: 3750          # ratio 1:4
  slope: 20
  bay_count: 8
  truss_type: "scissors"

profiles:
  top_chord: "HSS_150x150x6"
  bottom_chord: "HSS_125x125x5"
  web_diagonal: "HSS_100x100x4"
  material: "A500_Gr_B"

connections:
  type: "welded"
  gusset_thickness: 12

finishing: "paint"
interior_exposed: true   # Cercha vista
```

### Ventaja de Scissors

```
Altura libre interior = H_cercha × 0.6

Cercha convencional 15m: altura libre ~2.0m
Cercha scissors 15m:     altura libre ~3.5m
```

---

## Ejemplo 5: Hangar de Aviacion (Grandes Luces)

### Descripcion
Sistema de cerchas para hangar de 60m de luz libre.

### Configuracion

```yaml
geometry:
  span: 60000
  height: 4800          # ratio 1:12.5
  slope: 5
  bay_count: 24
  truss_type: "parallel_warren"

profiles:
  top_chord: "HSS_300x300x10"
  bottom_chord: "HSS_300x300x10"
  web_diagonal: "HSS_200x200x8"
  web_vertical: "HSS_150x150x6"
  material: "A572_Gr50"

connections:
  type: "bolted"        # Conexiones de campo
  gusset_thickness: 25
  bolt_diameter: 27
  bolt_grade: "A490"

secondary:
  purlins_spacing: 2500
  bracing: "X"

finishing: "galvanize"
```

### Estrategia de Fabricacion

```python
# Dividir cercha en 5 secciones
sections = [
    {"length": 12000, "weight": 2500},
    {"length": 12000, "weight": 2800},
    {"length": 12000, "weight": 3000},  # Centro
    {"length": 12000, "weight": 2800},
    {"length": 12000, "weight": 2500},
]

# Conexiones de campo
field_splices = 4  # Entre secciones
bolts_per_splice = 32  # Tornillos por empalme
```

---

## Ejemplo 6: Cercha sobre Curva

### Descripcion
Cercha que sigue una curva en planta.

### Configuracion

```python
import Rhino.Geometry as rg

# Crear curva base (arco)
arc = rg.Arc(
    rg.Point3d(0, 0, 0),
    rg.Point3d(10000, 2000, 0),
    rg.Point3d(20000, 0, 0)
)
base_curve = arc.ToNurbsCurve()

# Generar cercha sobre curva
truss = generator.generate(
    span=20000,
    height=2500,
    bay_count=12,
    truss_type='warren',
    base_curve=base_curve
)

# Los nodos siguen la curvatura
for node in truss.nodes:
    print(f"X={node.point.X:.0f}, Y={node.point.Y:.0f}, Z={node.point.Z:.0f}")
```

---

## Ejemplo 7: Optimizacion de Peso

### Descripcion
Proceso de optimizacion para minimizar peso.

### Codigo

```python
from E02_cercha import TrussOptimizer

optimizer = TrussOptimizer()

# Parametros a optimizar
design_space = {
    'height': (1500, 3000),      # rango de altura
    'bay_count': (6, 14),         # rango de modulos
    'truss_type': ['pratt', 'warren', 'howe']
}

# Restricciones
constraints = {
    'max_deflection': span / 240,
    'max_utilization': 0.90,
    'max_slenderness': 200
}

# Ejecutar optimizacion
result = optimizer.optimize(
    span=18000,
    loads={'dead': 0.5, 'live': 1.0},
    design_space=design_space,
    constraints=constraints,
    objective='weight'
)

print(f"Tipologia optima: {result.truss_type}")
print(f"Altura optima: {result.height} mm")
print(f"Modulos: {result.bay_count}")
print(f"Peso minimo: {result.weight:.0f} kg")
```

### Resultados de Optimizacion

| Tipologia | Altura | Modulos | Peso | Costo |
|-----------|--------|---------|------|-------|
| Pratt | 2000 | 10 | 720 kg | $81,000 |
| Warren | 1800 | 12 | 680 kg | $76,000 |
| Howe | 2200 | 8 | 750 kg | $84,000 |

**Optimo**: Warren, 12 modulos, altura 1800mm

---

## Ejemplo 8: Exportacion a Revit

### Descripcion
Flujo de exportacion completo a Revit.

### Codigo

```python
from E02_cercha import RevitExporter

# Generar cercha
truss = generator.generate(span=15000, truss_type='pratt')
profiles = selector.select_profiles(truss.member_data)

# Crear exportador
exporter = RevitExporter(
    family_name="BIMAC_Steel_Truss",
    category="Structural Framing"
)

# Exportar miembros
for i, member in enumerate(truss.member_data):
    profile = profiles[i].profile

    exporter.create_beam(
        start=member.line.From,
        end=member.line.To,
        profile_name=profile.name,
        parameters={
            'BIMAC_Member_Type': member.type.value,
            'BIMAC_Member_Force': forces[i],
            'BIMAC_Member_Utilization': profiles[i].utilization
        }
    )

# Crear schedule
exporter.create_schedule(
    name="BIMAC_Truss_Schedule",
    fields=[
        "Family and Type",
        "BIMAC_Member_Type",
        "Length",
        "BIMAC_Member_Force",
        "BIMAC_Member_Utilization"
    ],
    group_by="BIMAC_Member_Type"
)

# Exportar a IFC
exporter.export_ifc(
    path="exports/truss.ifc",
    include_properties=True
)
```

---

## Comparativa de Tipologias

### Para 18m de Luz

| Tipologia | Peso (kg) | Miembros | Nodos | Costo/kg |
|-----------|-----------|----------|-------|----------|
| Fink | 780 | 21 | 13 | $115 |
| Pratt | 720 | 27 | 15 | $108 |
| Howe | 750 | 27 | 15 | $110 |
| Warren | 680 | 19 | 11 | $105 |
| Fan | 820 | 23 | 13 | $118 |

**Recomendacion**: Warren para eficiencia de peso, Pratt para facilidad constructiva.

---

## Plantillas Rapidas

### Nave Industrial Pequena (12-18m)

```yaml
truss_type: "pratt"
height_ratio: 0.12
bay_count: 8
profile_type: "HSS"
connection: "welded"
finishing: "paint"
```

### Nave Industrial Grande (25-40m)

```yaml
truss_type: "parallel_warren"
height_ratio: 0.08
bay_count: 16
profile_type: "HSS"
connection: "bolted"
finishing: "galvanize"
```

### Cubierta Arquitectonica

```yaml
truss_type: "bowstring"
height_ratio: 0.12
bay_count: 12
profile_type: "PIPE"
connection: "welded"
finishing: "paint"
exposed: true
```

---

*Ejemplos v1.0 - E02 Cercha Parametrica*
