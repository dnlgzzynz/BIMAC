# Ejemplos de Uso - F01 Muro Cortina Parametrico

Casos de uso practicos y configuraciones tipicas.

---

## Ejemplo 1: Edificio de Oficinas Tipico

### Descripcion
Muro cortina para edificio corporativo de 15 niveles, orientacion sur.

### Configuracion

```yaml
geometry:
  module_width: 1500
  module_height: 3600
  u_divisions: auto
  v_divisions: auto

mullions:
  type: thermal
  width: 65
  depth: 150
  finish: powder_coat

panels:
  glass_type: double_low_e
  spandrel_height: 900
  panel_pattern: mixed
  vision_percent: 70

structural:
  max_span: 3600
  wind_load: 1.2
  seismic_zone: C

system:
  type: stick
  grade: standard
```

### Codigo Python

```python
from F01_muro_cortina import CurtainWallGenerator

# Configuracion
config = {
    "module_width": 1500,
    "module_height": 3600,
    "mullion_type": "thermal",
    "mullion_width": 65,
    "mullion_depth": 150,
    "glass_type": "double_low_e",
    "spandrel_height": 900,
    "panel_pattern": "mixed",
    "vision_percent": 70,
    "system_type": "stick",
    "material_grade": "standard"
}

# Generar
generator = CurtainWallGenerator()
result = generator.generate(surface, config)

# Resultados
print(f"Paneles de vision: {len(result.vision_panels)}")
print(f"Paneles de spandrel: {len(result.spandrel_panels)}")
print(f"Area total: {result.summary['total_area']:.2f} m2")
print(f"Costo estimado: ${result.cost.total:,.2f} MXN")
```

### Resultados Tipicos

| Metrica | Valor |
|---------|-------|
| Area total | 2,500 m2 |
| Vision | 70% |
| U-value promedio | 1.8 W/m2K |
| SHGC | 0.38 |
| Costo/m2 | $5,200 MXN |

---

## Ejemplo 2: Fachada Curva de Museo

### Descripcion
Muro cortina sobre superficie NURBS de doble curvatura.

### Configuracion

```yaml
geometry:
  surface: nurbs_surface
  u_divisions: 20
  v_divisions: 8
  module_width: 1200  # Mas pequeno para curvatura
  module_height: 2400

mullions:
  type: standard
  width: 50
  depth: 120
  finish: anodized_bronze

panels:
  glass_type: double_clear
  spandrel_height: 0  # Sin spandrel
  panel_pattern: vision
  vision_percent: 100

structural:
  max_span: 2400
  wind_load: 1.0
```

### Consideraciones Especiales

1. **Paneles curvos**: El sistema analiza la curvatura Gaussiana
   - Paneles con K < 0.0001: planos (fabricacion estandar)
   - Paneles con K < 0.001: curvatura simple (vidrio curvo en caliente)
   - Paneles con K > 0.001: doble curvatura (vidrio laminado curvo)

2. **Mullions flexibles**: En superficies curvas, los mullions siguen la curvatura

3. **Costo adicional**: Factor 1.25x - 1.65x por geometria curva

### Codigo

```python
# Analizar curvatura
from F01_muro_cortina import CurvatureAnalyzer

analyzer = CurvatureAnalyzer()
curvature_map = analyzer.analyze(surface, resolution=50)

# Clasificar paneles
panel_types = {
    'flat': curvature_map.flat_count,
    'single_curve': curvature_map.single_count,
    'double_curve': curvature_map.double_count
}

print(f"Paneles planos: {panel_types['flat']} ({panel_types['flat']/total*100:.1f}%)")
```

---

## Ejemplo 3: Torre de Gran Altura

### Descripcion
Sistema unitizado para torre de 45 niveles.

### Configuracion

```yaml
geometry:
  module_width: 1500
  module_height: 4200

mullions:
  type: structural
  width: 80
  depth: 200
  finish: pvdf

panels:
  glass_type: triple_low_e_argon
  panel_pattern: horizontal_bands
  vision_percent: 60

structural:
  max_span: 4200
  wind_load: 2.0  # Alta carga por altura
  seismic_zone: C
  deflection_limit: 200

system:
  type: unitized
  grade: premium
```

### Ventajas del Sistema Unitizado

1. **Instalacion rapida**: Paneles llegan ensamblados de fabrica
2. **Control de calidad**: Mejor hermeticidad
3. **Altura ilimitada**: Cada panel es independiente
4. **Menor mano de obra en sitio**

### Codigo

```python
# Verificar capacidad estructural
from F01_muro_cortina import MullionOptimizer

optimizer = MullionOptimizer(wind_load=2.0, max_deflection_ratio=200)

recommendation = optimizer.recommend_profile(
    span=4200,
    tributary_width=1500,
    glass_weight=45  # Triple glazing
)

print(f"Perfil recomendado: {recommendation['profile_type']}")
print(f"Profundidad requerida: {recommendation['depth']} mm")
```

---

## Ejemplo 4: Esquina de Edificio

### Descripcion
Muro cortina en esquina con angulo de 90 grados.

### Configuracion

```yaml
geometry:
  corner_angle: 90
  corner_treatment: mullion  # O: butt_joint, structural_corner

mullions:
  corner_mullion_width: 100  # Mas ancho en esquina
  corner_mullion_depth: 180
```

### Tratamientos de Esquina

| Tipo | Descripcion | Costo Rel. |
|------|-------------|------------|
| **mullion** | Mullion esquinero visible | 1.0x |
| **butt_joint** | Vidrio a tope con silicona | 1.4x |
| **structural_corner** | Esquina estructural | 1.6x |

### Codigo

```python
from F01_muro_cortina import CornerBuilder

corner = CornerBuilder()
corner_result = corner.build(
    surface_a=facade_north,
    surface_b=facade_east,
    angle=90,
    treatment='mullion',
    corner_mullion_width=100
)

# Mullion especial de esquina
corner_mullion = corner_result.corner_mullion
corner_panels = corner_result.corner_panels
```

---

## Ejemplo 5: Renovacion de Fachada

### Descripcion
Sustitucion de muro cortina existente, ajustandose a grid estructural.

### Configuracion

```yaml
geometry:
  grid_spacing_x: 7200  # Ejes estructurales
  grid_spacing_y: 3600
  offset_from_structure: 150

constraints:
  anchor_to_slab: true
  anchor_spacing: 1800
  max_deviation: 25  # mm de tolerancia

existing:
  preserve_anchors: false
  demolition_required: true
```

### Proceso

1. **Relevamiento**: Escaneo 3D de estructura existente
2. **Ajuste de grid**: Adaptar modulos a ejes existentes
3. **Verificacion de anclajes**: Capacidad de losas

### Codigo

```python
from F01_muro_cortina import ExistingStructureAdapter

adapter = ExistingStructureAdapter()

# Cargar nube de puntos de escaneo
adapter.load_point_cloud("scan_fachada.pts")

# Detectar grid estructural
detected_grid = adapter.detect_grid(tolerance=50)

# Ajustar muro cortina
adjusted_result = adapter.fit_curtain_wall(
    target_module_width=1500,
    target_module_height=3600,
    grid=detected_grid
)

print(f"Modulo ajustado: {adjusted_result.actual_width} x {adjusted_result.actual_height}")
```

---

## Ejemplo 6: Integracion con Analisis Solar

### Descripcion
Optimizacion de vision y spandrel segun orientacion.

### Configuracion

```yaml
analysis:
  location: "Mexico City"
  latitude: 19.4326
  longitude: -99.1332

optimization:
  target_daylight: 2.0  # % de area de piso
  max_solar_gain: 100   # W/m2
  auto_adjust_vision: true
```

### Codigo con Ladybug

```python
from F01_muro_cortina import SolarOptimizer

optimizer = SolarOptimizer(
    latitude=19.4326,
    longitude=-99.1332
)

# Analizar cada fachada
for facade in facades:
    orientation = optimizer.get_orientation(facade.normal)
    recommendation = optimizer.recommend_vision_percent(orientation)

    print(f"Fachada {orientation}: {recommendation['vision_percent']}% vision")
    print(f"  Vidrio recomendado: {recommendation['recommended_glass']}")
    print(f"  Notas: {recommendation['notes']}")
```

### Resultados por Orientacion

| Orientacion | Vision | Vidrio | SHGC Max |
|-------------|--------|--------|----------|
| Norte | 80% | double_clear | 0.70 |
| Este | 65% | double_low_e | 0.40 |
| Sur | 50% | double_low_e | 0.35 |
| Oeste | 55% | double_low_e | 0.38 |

---

## Ejemplo 7: Exportacion a Revit

### Descripcion
Flujo completo de exportacion usando Rhino.inside.Revit.

### Codigo

```python
# En Grasshopper con Rhino.inside.Revit
from F01_muro_cortina import RevitExporter

exporter = RevitExporter(
    family_name="BIMAC_CW_Panel_Adaptive",
    category="Curtain Panels"
)

# Exportar todos los paneles
export_result = exporter.export_panels(
    vision_panels=result.vision_panels,
    spandrel_panels=result.spandrel_panels,
    panel_data=result.panel_data,
    mullions=result.mullions,
    transoms=result.transoms
)

# Crear schedule
exporter.create_schedule(
    schedule_name="BIMAC_CW_Schedule",
    fields=[
        "BIMAC_CW_PanelType",
        "BIMAC_CW_Area",
        "BIMAC_CW_UValue",
        "BIMAC_CW_Cost"
    ]
)

# Exportar a IFC
exporter.export_ifc(
    output_path="exports/curtain_wall.ifc",
    version="IFC4",
    include_properties=True
)
```

---

## Ejemplo 8: Calculo de Costos Detallado

### Descripcion
Desglose completo de presupuesto.

### Codigo

```python
from F01_muro_cortina import CostCalculator

calculator = CostCalculator(currency='MXN')

# Calcular costos
cost_result = calculator.calculate(
    mullions_data=result.mullion_data,
    transoms_data=result.transom_data,
    panels_data=result.panel_data,
    panel_summary=result.summary,
    system_type='stick',
    material_grade='standard'
)

# Generar reporte
report = calculator.generate_report(cost_result)
print(report)

# Exportar a Excel
calculator.export_excel(
    cost_result,
    output_path="exports/presupuesto_fachada.xlsx"
)
```

### Ejemplo de Reporte

```
======================================================================
REPORTE DE COSTOS - MURO CORTINA PARAMETRICO
======================================================================
Sistema: STICK
Grado: STANDARD
Area total: 500.00 m2
----------------------------------------------------------------------

ALUMINIO
----------------------------------------
  Perfiles mullion                  750.00 kg   x $   120.00 = $   90,000.00
  Perfiles transom                  280.00 kg   x $   120.00 = $   33,600.00
  Subtotal                                                    $  123,600.00

ACABADOS
----------------------------------------
  Powder Coat                       450.00 m2   x $   320.00 = $  144,000.00
  Subtotal                                                    $  144,000.00

VIDRIO
----------------------------------------
  Double Low E                      350.00 m2   x $ 1,100.00 = $  385,000.00
  Subtotal                                                    $  385,000.00

SPANDREL
----------------------------------------
  Insulated Metal                   150.00 m2   x $   780.00 = $  117,000.00
  Subtotal                                                    $  117,000.00

MANO DE OBRA
----------------------------------------
  Instalacion sistema stick         500.00 m2   x $   850.00 = $  425,000.00
  Subtotal                                                    $  425,000.00

======================================================================
                                            TOTAL $ 1,456,000.00 MXN
                                      COSTO POR M2 $    2,912.00 MXN/m2
======================================================================
```

---

## Plantillas de Configuracion

### Oficinas Clase A

```yaml
# config_oficinas_a.yaml
name: "Oficinas Clase A"
system_type: unitized
material_grade: premium
glass_type: triple_low_e_argon
mullion_type: thermal
vision_percent: 65
```

### Comercial Economico

```yaml
# config_comercial.yaml
name: "Comercial Economico"
system_type: stick
material_grade: basic
glass_type: double_clear
mullion_type: standard
vision_percent: 75
```

### Residencial Alta Gama

```yaml
# config_residencial.yaml
name: "Residencial Premium"
system_type: structural_glazing
material_grade: premium
glass_type: double_low_e_argon
mullion_type: thermal
vision_percent: 85
```

---

*Ejemplos v1.0 - F01 Muro Cortina Parametrico*
