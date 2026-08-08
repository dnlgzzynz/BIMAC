# PROJECT.md - Especificaciones Técnicas

**Proyecto:** Cubierta Orgánica de Museo
**Código:** MUSEO-CUBIERTA-001
**Versión:** 1.0.0

---

## 1. Especificaciones de Diseño

### 1.1 Geometría Base

| Parámetro | Símbolo | Valor | Tolerancia | Unidad |
|-----------|---------|-------|------------|--------|
| Ancho museo | W | 15.0 | ±0.5 | m |
| Largo museo | L | 26.0 | ±0.5 | m |
| Altura cenit | H | 8.5 | ±0.2 | m |
| Radio curvatura mín | Rmin | 3.0 | - | m |
| Pendiente mínima | Smin | 2.0 | - | % |

### 1.2 Restricciones Estructurales

```
┌────────────────────────────────────────────────────────────┐
│                   RESTRICCIONES CRÍTICAS                   │
├────────────────────────────────────────────────────────────┤
│ 1. Luz libre máxima:     15.0 m                           │
│    - Medida entre apoyos estructurales                     │
│    - Validación automática en GH                           │
│                                                            │
│ 2. Flecha máxima:        L/250 = 104 mm                   │
│    - Para combinación de cargas de servicio                │
│                                                            │
│ 3. Carga de diseño:                                        │
│    - Peso propio:        0.25 kN/m²                        │
│    - Carga viva:         0.40 kN/m²                        │
│    - Viento:             0.50 kN/m² (presión)              │
│    - Total:              1.15 kN/m²                        │
│                                                            │
│ 4. Drenaje:                                                │
│    - Pendiente mínima:   2%                                │
│    - Canalones cada:     6.0 m máximo                      │
└────────────────────────────────────────────────────────────┘
```

### 1.3 Módulo de Panel

```
Panel Estándar:
┌──────────────────┐
│                  │
│   2000 mm        │  Área: 3.0 m²
│                  │  Peso: ~15 kg (policarbonato 16mm)
│                  │
└──────────────────┘
      1500 mm

Tolerancias de fabricación:
- Longitud: ±2 mm
- Ancho: ±2 mm
- Planaridad: ≤5 mm desviación
```

---

## 2. Materiales

### 2.1 Estructura Principal

| Material | Especificación | Uso |
|----------|----------------|-----|
| Acero estructural | ASTM A500 Gr. B | Perfiles tubulares |
| Sección típica | HSS 150×150×6 | Cerchas principales |
| Acabado | Galvanizado en caliente | Protección exterior |
| Conexiones | ASTM A325 | Pernos de alta resistencia |

### 2.2 Paneles de Cubierta

| Tipo | Material | Espesor | U-Value | Transmitancia |
|------|----------|---------|---------|---------------|
| Plano | Policarbonato celular | 16 mm | 2.3 W/m²K | 65% |
| Curvo simple | Policarbonato celular | 16 mm | 2.3 W/m²K | 60% |
| Doble curva | Policarbonato sólido | 10 mm | 4.5 W/m²K | 75% |

### 2.3 Costos de Materiales

```python
# Estructura de costos (MXN/m²)
COST_STRUCTURE = {
    "panel_flat": 450.0,        # Policarbonato plano
    "panel_single_curve": 680.0, # Termoformado simple
    "panel_double_curve": 1250.0, # Molde CNC
    "structure_factor": 0.25,    # 25% del costo de paneles
    "installation_factor": 0.15, # 15% del subtotal
}
```

---

## 3. Lógica de Grasshopper

### 3.1 Flujo de Componentes

```
[INPUT]
   │
   ├── Number Sliders (Ancho, Largo, Altura, Tensión)
   │
   ▼
[GEOMETRÍA BASE]
   │
   ├── Curve: Curva guía inferior
   ├── Curve: Curva guía superior (cenit)
   ├── Loft: Superficie principal
   │
   ▼
[VALIDACIÓN ESTRUCTURAL]
   │
   ├── Python: Evaluar luz libre en grid
   ├── Condition: max_span ≤ 15000 mm
   ├── Alert: Panel de advertencia si excede
   │
   ▼
[PANELIZACIÓN]
   │
   ├── Lunchbox: Quad Panel (U×V divisiones)
   ├── Pufferfish: Panel Planarize
   ├── Python: Clasificar por curvatura gaussiana
   │
   ▼
[ANÁLISIS DE COSTOS]
   │
   ├── Python: Calcular área por tipo
   ├── Python: Aplicar costos unitarios
   ├── Panel: Reporte de costos
   ├── Condition: total ≤ presupuesto
   │
   ▼
[EXPORTACIÓN]
   │
   ├── Rhino.inside.Revit: Add Adaptive Component
   ├── Parámetros: Type, Cost, Material
   └── Schedules automáticos
```

### 3.2 Script: Validación Estructural

```python
"""
validate_span.py
Valida que la luz libre no exceda el máximo permitido.

Inputs:
    surface (Surface): Superficie de cubierta
    max_allowed (float): Luz máxima permitida en mm

Outputs:
    is_valid (bool): True si cumple restricción
    max_span (float): Luz máxima encontrada
    warning (str): Mensaje de estado
    critical_points (List[Point3d]): Puntos críticos
"""

import Rhino.Geometry as rg

# Constantes
MAX_SPAN_ALLOWED = 15000  # mm
SAMPLE_RESOLUTION = 10

def validate_structural_span(surface, max_allowed=MAX_SPAN_ALLOWED):
    """
    Evalúa la luz libre máxima en la superficie.

    Args:
        surface: Superficie NURBS
        max_allowed: Luz máxima permitida (mm)

    Returns:
        tuple: (is_valid, max_span, warning, critical_points)
    """
    if surface is None:
        return False, 0, "Error: Superficie no válida", []

    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)

    max_span = 0
    critical_points = []

    # Muestrear superficie
    for i in range(SAMPLE_RESOLUTION + 1):
        u_param = u_domain.ParameterAt(i / SAMPLE_RESOLUTION)
        for j in range(SAMPLE_RESOLUTION + 1):
            v_param = v_domain.ParameterAt(j / SAMPLE_RESOLUTION)

            pt = surface.PointAt(u_param, v_param)

            # Calcular distancia mínima a bordes
            distances = [
                pt.DistanceTo(surface.PointAt(u_domain.Min, v_param)),
                pt.DistanceTo(surface.PointAt(u_domain.Max, v_param)),
                pt.DistanceTo(surface.PointAt(u_param, v_domain.Min)),
                pt.DistanceTo(surface.PointAt(u_param, v_domain.Max))
            ]

            min_dist = min(distances)

            if min_dist > max_span:
                max_span = min_dist
                critical_points = [pt]
            elif abs(min_dist - max_span) < 1:  # Tolerancia 1mm
                critical_points.append(pt)

    # Validar
    is_valid = max_span <= max_allowed

    if is_valid:
        warning = f"OK: Luz libre {max_span/1000:.2f} m <= {max_allowed/1000:.1f} m"
    else:
        warning = f"EXCEDE: Luz libre {max_span/1000:.2f} m > {max_allowed/1000:.1f} m"

    return is_valid, max_span, warning, critical_points


# Ejecutar
is_valid, max_span, warning, critical_points = validate_structural_span(
    surface, MAX_SPAN_ALLOWED
)

# Outputs para Grasshopper
a = is_valid
b = max_span
c = warning
d = critical_points
```

### 3.3 Script: Clasificación de Curvatura

```python
"""
classify_panels.py
Clasifica paneles por curvatura gaussiana para optimización de costos.

Inputs:
    panels (List[Brep]): Lista de paneles

Outputs:
    flat_panels (List[Brep]): Paneles planos
    single_curve (List[Brep]): Curvatura simple
    double_curve (List[Brep]): Doble curvatura
    panel_types (List[str]): Tipo de cada panel
"""

import Rhino.Geometry as rg

# Umbrales de curvatura gaussiana
THRESHOLD_FLAT = 0.0001
THRESHOLD_SINGLE = 0.001


def get_gaussian_curvature(surface):
    """
    Calcula curvatura gaussiana en el centro de la superficie.

    Args:
        surface: Superficie a evaluar

    Returns:
        float: Valor absoluto de curvatura gaussiana
    """
    u_mid = surface.Domain(0).Mid
    v_mid = surface.Domain(1).Mid

    curvature = surface.CurvatureAt(u_mid, v_mid)

    if curvature is None:
        return 0.0

    return abs(curvature.Gaussian)


def classify_panels(panels):
    """
    Clasifica paneles por tipo de curvatura.

    Args:
        panels: Lista de Breps (paneles)

    Returns:
        tuple: (flat, single_curve, double_curve, types)
    """
    flat = []
    single_curve = []
    double_curve = []
    types = []

    for panel in panels:
        if not isinstance(panel, rg.Brep):
            continue

        if panel.Faces.Count == 0:
            continue

        face = panel.Faces[0]
        gauss = get_gaussian_curvature(face)

        if gauss < THRESHOLD_FLAT:
            flat.append(panel)
            types.append("flat")
        elif gauss < THRESHOLD_SINGLE:
            single_curve.append(panel)
            types.append("single_curve")
        else:
            double_curve.append(panel)
            types.append("double_curve")

    return flat, single_curve, double_curve, types


# Ejecutar
flat_panels, single_curve, double_curve, panel_types = classify_panels(panels)

# Outputs
a = flat_panels
b = single_curve
c = double_curve
d = panel_types
```

### 3.4 Script: Calculadora de Costos

```python
"""
cost_calculator.py
Calcula costos totales basados en clasificación de paneles.

Inputs:
    flat_panels (List[Brep]): Paneles planos
    single_curve (List[Brep]): Curvatura simple
    double_curve (List[Brep]): Doble curvatura
    budget (float): Presupuesto disponible

Outputs:
    report (str): Reporte detallado
    total_cost (float): Costo total
    is_within_budget (bool): Cumple presupuesto
    cost_breakdown (dict): Desglose de costos
"""

import Rhino.Geometry as rg

# Costos unitarios (MXN/m²)
COSTS = {
    "flat": 450.0,
    "single_curve": 680.0,
    "double_curve": 1250.0,
}

STRUCTURE_FACTOR = 0.25  # 25% adicional para estructura


def get_panel_area(panel):
    """Calcula área de un panel en m²."""
    if panel is None:
        return 0.0

    props = rg.AreaMassProperties.Compute(panel)
    if props is None:
        return 0.0

    # Convertir de mm² a m²
    return props.Area / 1000000.0


def calculate_costs(flat, single, double, budget):
    """
    Calcula costos totales del proyecto.

    Args:
        flat: Lista de paneles planos
        single: Lista de paneles curvatura simple
        double: Lista de paneles doble curvatura
        budget: Presupuesto disponible

    Returns:
        tuple: (report, total, is_within_budget, breakdown)
    """
    # Calcular áreas
    flat_area = sum(get_panel_area(p) for p in flat)
    single_area = sum(get_panel_area(p) for p in single)
    double_area = sum(get_panel_area(p) for p in double)

    # Calcular costos por tipo
    cost_flat = flat_area * COSTS["flat"]
    cost_single = single_area * COSTS["single_curve"]
    cost_double = double_area * COSTS["double_curve"]

    subtotal_panels = cost_flat + cost_single + cost_double
    cost_structure = subtotal_panels * STRUCTURE_FACTOR
    total_cost = subtotal_panels + cost_structure

    is_within_budget = total_cost <= budget
    margin = budget - total_cost

    # Generar reporte
    report = f"""
================================================================================
                         ANÁLISIS DE COSTOS - CUBIERTA
================================================================================

PANELES:
--------------------------------------------------------------------------------
  Tipo              | Cantidad |  Área (m²) |  Costo/m² |     Subtotal
--------------------------------------------------------------------------------
  Planos            |   {len(flat):5d}  |  {flat_area:8.1f}  |   ${COSTS['flat']:6.0f}  |  ${cost_flat:12,.0f}
  Curvatura Simple  |   {len(single):5d}  |  {single_area:8.1f}  |   ${COSTS['single_curve']:6.0f}  |  ${cost_single:12,.0f}
  Doble Curvatura   |   {len(double):5d}  |  {double_area:8.1f}  |   ${COSTS['double_curve']:6.0f}  |  ${cost_double:12,.0f}
--------------------------------------------------------------------------------
  SUBTOTAL PANELES  |   {len(flat)+len(single)+len(double):5d}  |  {flat_area+single_area+double_area:8.1f}  |           |  ${subtotal_panels:12,.0f}
--------------------------------------------------------------------------------

ESTRUCTURA:
--------------------------------------------------------------------------------
  Estructura metálica (25% de paneles)              |  ${cost_structure:12,.0f}
--------------------------------------------------------------------------------

================================================================================
  TOTAL PROYECTO                                    |  ${total_cost:12,.0f} MXN
================================================================================
  Presupuesto                                       |  ${budget:12,.0f} MXN
  {'DENTRO DE PRESUPUESTO' if is_within_budget else 'EXCEDE PRESUPUESTO'}
  Margen: ${margin:,.0f} MXN ({margin/budget*100:.1f}%)
================================================================================
"""

    breakdown = {
        "flat": {"qty": len(flat), "area": flat_area, "cost": cost_flat},
        "single": {"qty": len(single), "area": single_area, "cost": cost_single},
        "double": {"qty": len(double), "area": double_area, "cost": cost_double},
        "structure": cost_structure,
        "total": total_cost,
        "margin": margin,
    }

    return report, total_cost, is_within_budget, breakdown


# Ejecutar
report, total_cost, is_within_budget, cost_breakdown = calculate_costs(
    flat_panels, single_curve, double_curve, budget
)

# Outputs
a = report
b = total_cost
c = is_within_budget
d = cost_breakdown
```

---

## 4. Integración Revit

### 4.1 Familia Adaptativa

**Nombre:** `Cubierta_Panel_Adaptive.rfa`
**Template:** `Generic Model Adaptive.rft`

**Parámetros de Instancia:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `BIMAC_PanelType` | Text | flat / single_curve / double_curve |
| `BIMAC_CostPerM2` | Currency | Costo por metro cuadrado |
| `BIMAC_TotalCost` | Currency | Costo total del panel |
| `BIMAC_Material` | Text | Tipo de policarbonato |
| `BIMAC_UValue` | Number | Coeficiente térmico |
| `BIMAC_PanelID` | Text | Identificador único |

### 4.2 Script de Exportación RiR

```python
"""
revit_exporter.py
Exporta paneles de Grasshopper a Revit como Adaptive Components.

Requiere: Rhino.inside.Revit activo
"""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RhinoInside.Revit')

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Rhino.Geometry as rg

# Configuración
FAMILY_NAME = "Cubierta_Panel_Adaptive"
MM_TO_FEET = 1.0 / 304.8


def export_to_revit(panels, panel_types, costs):
    """
    Exporta paneles a Revit como Adaptive Components.

    Args:
        panels: Lista de Breps
        panel_types: Tipo de cada panel
        costs: Costo de cada panel

    Returns:
        list: IDs de elementos creados
    """
    doc = DocumentManager.Instance.CurrentDBDocument
    created_ids = []

    # Obtener familia
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol)
    family_symbol = None

    for fs in collector:
        if fs.FamilyName == FAMILY_NAME:
            family_symbol = fs
            break

    if family_symbol is None:
        raise Exception(f"Familia '{FAMILY_NAME}' no encontrada")

    if not family_symbol.IsActive:
        family_symbol.Activate()

    # Crear elementos
    TransactionManager.Instance.EnsureInTransaction(doc)

    for i, panel in enumerate(panels):
        if not isinstance(panel, rg.Brep):
            continue

        # Extraer vértices
        vertices = []
        edges = panel.Edges
        for edge in edges[:4]:  # Solo 4 esquinas
            pt = edge.PointAtStart
            xyz = XYZ(
                pt.X * MM_TO_FEET,
                pt.Y * MM_TO_FEET,
                pt.Z * MM_TO_FEET
            )
            vertices.append(xyz)

        # Crear Adaptive Component
        try:
            adaptive = AdaptiveComponentInstanceUtils.CreateAdaptiveComponentInstance(
                doc, family_symbol
            )

            # Asignar puntos
            placement_ids = AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(
                adaptive
            )

            for j, pt_id in enumerate(placement_ids):
                if j < len(vertices):
                    pt_element = doc.GetElement(pt_id)
                    pt_element.Position = vertices[j]

            # Asignar parámetros
            set_parameter(adaptive, "BIMAC_PanelType", panel_types[i])
            set_parameter(adaptive, "BIMAC_TotalCost", costs[i])
            set_parameter(adaptive, "BIMAC_PanelID", f"PANEL-{i+1:04d}")

            created_ids.append(adaptive.Id.IntegerValue)

        except Exception as ex:
            print(f"Error en panel {i}: {ex}")

    TransactionManager.Instance.TransactionTaskDone()

    return created_ids


def set_parameter(element, param_name, value):
    """Establece valor de parámetro en elemento."""
    param = element.LookupParameter(param_name)
    if param is not None and not param.IsReadOnly:
        if isinstance(value, str):
            param.Set(value)
        elif isinstance(value, (int, float)):
            param.Set(float(value))


# Ejecutar exportación
if panels and panel_types and costs:
    created_ids = export_to_revit(panels, panel_types, costs)
    result = f"Creados {len(created_ids)} paneles en Revit"
else:
    result = "Error: Datos de entrada incompletos"

# Output
a = result
b = created_ids
```

---

## 5. Automatización n8n

### 5.1 Workflow: Notificación de Costos

```json
{
  "name": "Cubierta - Cost Update Notifier",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "cubierta-cost-update",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Process Data",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const data = $input.first().json;\nconst budget = 280000;\nconst isOver = data.totalCost > budget;\n\nreturn [{\n  json: {\n    ...data,\n    isOverBudget: isOver,\n    margin: budget - data.totalCost,\n    marginPercent: ((budget - data.totalCost) / budget * 100).toFixed(1)\n  }\n}];"
      }
    },
    {
      "name": "Update Airtable",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "create",
        "baseId": "{{ $env.AIRTABLE_BASE_ID }}",
        "tableId": "CostHistory",
        "fields": {
          "Timestamp": "={{ $now }}",
          "TotalCost": "={{ $json.totalCost }}",
          "PanelCount": "={{ $json.panelCount }}",
          "IsOverBudget": "={{ $json.isOverBudget }}"
        }
      }
    },
    {
      "name": "Send Slack Alert",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#bim-alerts",
        "text": "Cubierta Museo - Actualización de Costos:\nTotal: ${{ $json.totalCost }} MXN\nMargen: {{ $json.marginPercent }}%\n{{ $json.isOverBudget ? 'EXCEDE PRESUPUESTO' : 'Dentro de presupuesto' }}"
      }
    }
  ]
}
```

---

## 6. Schedules de Revit

### 6.1 Schedule de Paneles

**Nombre:** `BIMAC_Cubierta_Paneles`
**Categoría:** Generic Models

**Campos:**

| Campo | Fuente | Formato |
|-------|--------|---------|
| BIMAC_PanelID | Parameter | Text |
| BIMAC_PanelType | Parameter | Text |
| Area | Built-in | m² (2 decimales) |
| BIMAC_CostPerM2 | Parameter | Currency |
| BIMAC_TotalCost | Parameter | Currency |
| BIMAC_Material | Parameter | Text |

**Totales:**
- Count (Cantidad de paneles)
- Sum (Area)
- Sum (BIMAC_TotalCost)

### 6.2 Schedule de Resumen de Costos

**Nombre:** `BIMAC_Cubierta_Resumen`

```
╔══════════════════════════════════════════════════════════╗
║              RESUMEN DE COSTOS - CUBIERTA               ║
╠══════════════════════════════════════════════════════════╣
║ Paneles Planos:         101 uds    $136,350.00 MXN     ║
║ Paneles Curvatura Simple: 23 uds    $47,070.00 MXN     ║
║ Paneles Doble Curvatura:   6 uds    $22,500.00 MXN     ║
╠══════════════════════════════════════════════════════════╣
║ Subtotal Paneles:       130 uds   $205,920.00 MXN      ║
║ Estructura (25%):                   $51,480.00 MXN      ║
╠══════════════════════════════════════════════════════════╣
║ TOTAL:                             $257,400.00 MXN      ║
║ Presupuesto:                       $280,000.00 MXN      ║
║ Margen:                             $22,600.00 MXN      ║
╚══════════════════════════════════════════════════════════╝
```

---

## 7. Control de Calidad

### 7.1 Checklist Pre-Fabricación

```markdown
## QA Checklist - Cubierta Museo

### Geometría
- [ ] Luz libre ≤ 15m verificada
- [ ] Pendiente mínima ≥ 2% en todos los puntos
- [ ] Sin auto-intersecciones en superficie
- [ ] Paneles sin solapes

### Panelización
- [ ] Módulos dentro de tolerancia (±2mm)
- [ ] Curvatura clasificada correctamente
- [ ] IDs únicos asignados

### Costos
- [ ] Total ≤ presupuesto
- [ ] Desglose por tipo verificado
- [ ] Margen documentado

### BIM
- [ ] Todos los paneles en Revit
- [ ] Parámetros asignados correctamente
- [ ] Schedules generados
- [ ] IFC exportado

### Documentación
- [ ] Planos de fabricación
- [ ] Despieces por panel
- [ ] Manual de instalación
```

### 7.2 Tolerancias de Fabricación

| Elemento | Tolerancia | Verificación |
|----------|------------|--------------|
| Longitud panel | ±2 mm | Cinta métrica |
| Ancho panel | ±2 mm | Cinta métrica |
| Planaridad | ≤5 mm | Regla 2m |
| Curvatura | ±R 50mm | Template |
| Posición fijación | ±3 mm | Plantilla |

---

## 8. Referencias

### Documentación Técnica

- [Rhino.inside.Revit Guide](https://www.rhino3d.com/inside/revit/1.0/guides/)
- [Lunchbox Documentation](https://www.food4rhino.com/en/app/lunchbox)
- [Revit API Reference](https://www.revitapidocs.com/)

### Normativas

- **NMX-C-406-ONNCCE** - Estructuras de acero
- **ISO 19650-2:2018** - BIM Information Management
- **ASTM A500** - Perfiles tubulares de acero

### Papers de Referencia

- Pottmann et al. (2007): "Architectural Geometry"
- Schek, H.J. (1974): "The force density method for form finding"

---

**Última actualización:** 2025-12-27
**Autor:** BIMAC - BIM Advance Consulting
