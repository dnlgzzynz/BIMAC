"""
cost_calculator.py
Calculadora de costos para cubierta paramétrica.

Proyecto: Cubierta Orgánica de Museo
Autor: BIMAC
Versión: 1.0.0

Uso en Grasshopper:
    1. Agregar componente "Python Script"
    2. Copiar este código
    3. Conectar inputs:
       - flat_panels (List[Brep]): Paneles planos
       - single_curve (List[Brep]): Paneles curvatura simple
       - double_curve (List[Brep]): Paneles doble curvatura
       - budget (float): Presupuesto disponible (MXN)
    4. Outputs: report, total_cost, is_within_budget, breakdown_json

Inputs:
    flat_panels (List[Brep]): Paneles clasificados como planos
    single_curve (List[Brep]): Paneles con curvatura simple
    double_curve (List[Brep]): Paneles con doble curvatura
    budget (float): Presupuesto máximo en MXN

Outputs:
    report (str): Reporte de costos formateado
    total_cost (float): Costo total del proyecto
    is_within_budget (bool): True si está dentro del presupuesto
    breakdown_json (str): Desglose en formato JSON
"""

import Rhino.Geometry as rg
import json
from collections import namedtuple

# =============================================================================
# CONFIGURACIÓN DE COSTOS
# =============================================================================

# Costos unitarios por tipo de panel (MXN/m²)
COST_CONFIG = {
    "flat": {
        "name": "Panel Plano",
        "cost_per_m2": 450.0,
        "material": "Policarbonato celular 16mm",
        "fabrication": "Corte CNC estándar"
    },
    "single_curve": {
        "name": "Curvatura Simple",
        "cost_per_m2": 680.0,
        "material": "Policarbonato celular 16mm",
        "fabrication": "Termoformado en caliente"
    },
    "double_curve": {
        "name": "Doble Curvatura",
        "cost_per_m2": 1250.0,
        "material": "Policarbonato sólido 10mm",
        "fabrication": "Molde CNC + termoformado"
    }
}

# Factores adicionales
STRUCTURE_FACTOR = 0.25      # 25% del costo de paneles para estructura
INSTALLATION_FACTOR = 0.15   # 15% del subtotal para instalación
CONTINGENCY_FACTOR = 0.10    # 10% de contingencia

# Presupuesto por defecto
DEFAULT_BUDGET = 280000.0  # MXN


# =============================================================================
# ESTRUCTURAS DE DATOS
# =============================================================================

CostBreakdown = namedtuple('CostBreakdown', [
    'panel_type',
    'quantity',
    'total_area',
    'cost_per_m2',
    'subtotal'
])

ProjectCost = namedtuple('ProjectCost', [
    'panels_cost',
    'structure_cost',
    'installation_cost',
    'contingency',
    'total',
    'budget',
    'margin',
    'margin_percent',
    'is_within_budget'
])


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================

def calculate_panel_area(panel):
    """
    Calcula el área de un panel en metros cuadrados.

    Args:
        panel (Brep): Panel a medir

    Returns:
        float: Área en m²
    """
    if panel is None:
        return 0.0

    try:
        props = rg.AreaMassProperties.Compute(panel)
        if props is None:
            return 0.0

        # Rhino trabaja en mm, convertir a m²
        area_mm2 = props.Area
        area_m2 = area_mm2 / 1000000.0  # mm² a m²

        return area_m2
    except Exception:
        return 0.0


def calculate_total_area(panels):
    """
    Calcula el área total de una lista de paneles.

    Args:
        panels (List[Brep]): Lista de paneles

    Returns:
        float: Área total en m²
    """
    if panels is None:
        return 0.0

    return sum(calculate_panel_area(p) for p in panels)


def calculate_cost_breakdown(panels, panel_type):
    """
    Calcula el desglose de costos para un tipo de panel.

    Args:
        panels (List[Brep]): Lista de paneles
        panel_type (str): Tipo de panel ('flat', 'single_curve', 'double_curve')

    Returns:
        CostBreakdown: Desglose de costos
    """
    if panels is None:
        panels = []

    config = COST_CONFIG.get(panel_type, COST_CONFIG["flat"])

    quantity = len(panels)
    total_area = calculate_total_area(panels)
    cost_per_m2 = config["cost_per_m2"]
    subtotal = total_area * cost_per_m2

    return CostBreakdown(
        panel_type=panel_type,
        quantity=quantity,
        total_area=total_area,
        cost_per_m2=cost_per_m2,
        subtotal=subtotal
    )


def calculate_project_cost(flat, single, double, budget=DEFAULT_BUDGET):
    """
    Calcula el costo total del proyecto.

    Args:
        flat (List[Brep]): Paneles planos
        single (List[Brep]): Paneles curvatura simple
        double (List[Brep]): Paneles doble curvatura
        budget (float): Presupuesto disponible

    Returns:
        tuple: (ProjectCost, dict[breakdowns])
    """
    # Calcular desglose por tipo
    flat_breakdown = calculate_cost_breakdown(flat, "flat")
    single_breakdown = calculate_cost_breakdown(single, "single_curve")
    double_breakdown = calculate_cost_breakdown(double, "double_curve")

    breakdowns = {
        "flat": flat_breakdown,
        "single_curve": single_breakdown,
        "double_curve": double_breakdown
    }

    # Costo total de paneles
    panels_cost = (
        flat_breakdown.subtotal +
        single_breakdown.subtotal +
        double_breakdown.subtotal
    )

    # Costos adicionales
    structure_cost = panels_cost * STRUCTURE_FACTOR
    subtotal_before_install = panels_cost + structure_cost

    installation_cost = subtotal_before_install * INSTALLATION_FACTOR
    subtotal_before_contingency = subtotal_before_install + installation_cost

    contingency = subtotal_before_contingency * CONTINGENCY_FACTOR

    # Total final
    total = subtotal_before_contingency + contingency

    # Margen
    margin = budget - total
    margin_percent = (margin / budget * 100) if budget > 0 else 0
    is_within_budget = total <= budget

    project_cost = ProjectCost(
        panels_cost=panels_cost,
        structure_cost=structure_cost,
        installation_cost=installation_cost,
        contingency=contingency,
        total=total,
        budget=budget,
        margin=margin,
        margin_percent=margin_percent,
        is_within_budget=is_within_budget
    )

    return project_cost, breakdowns


def format_currency(amount):
    """Formatea un número como moneda MXN."""
    return f"${amount:,.2f}"


def generate_cost_report(project_cost, breakdowns):
    """
    Genera un reporte detallado de costos.

    Args:
        project_cost (ProjectCost): Costos del proyecto
        breakdowns (dict): Desglose por tipo de panel

    Returns:
        str: Reporte formateado
    """
    flat = breakdowns["flat"]
    single = breakdowns["single_curve"]
    double = breakdowns["double_curve"]

    total_panels = flat.quantity + single.quantity + double.quantity
    total_area = flat.total_area + single.total_area + double.total_area

    status = "DENTRO DE PRESUPUESTO" if project_cost.is_within_budget else "EXCEDE PRESUPUESTO"
    status_indicator = "OK" if project_cost.is_within_budget else "ALERTA"

    report = f"""
================================================================================
                    ANÁLISIS DE COSTOS - CUBIERTA MUSEO
================================================================================

DESGLOSE POR TIPO DE PANEL:
--------------------------------------------------------------------------------
  Tipo                 | Cantidad |  Área (m²) |   Costo/m²  |      Subtotal
--------------------------------------------------------------------------------
  Paneles Planos       |   {flat.quantity:5d}  |  {flat.total_area:8.2f}  |  {format_currency(flat.cost_per_m2):>10}  |  {format_currency(flat.subtotal):>14}
  Curvatura Simple     |   {single.quantity:5d}  |  {single.total_area:8.2f}  |  {format_currency(single.cost_per_m2):>10}  |  {format_currency(single.subtotal):>14}
  Doble Curvatura      |   {double.quantity:5d}  |  {double.total_area:8.2f}  |  {format_currency(double.cost_per_m2):>10}  |  {format_currency(double.subtotal):>14}
--------------------------------------------------------------------------------
  SUBTOTAL PANELES     |   {total_panels:5d}  |  {total_area:8.2f}  |            |  {format_currency(project_cost.panels_cost):>14}
--------------------------------------------------------------------------------

COSTOS ADICIONALES:
--------------------------------------------------------------------------------
  Estructura metálica ({STRUCTURE_FACTOR*100:.0f}%)                    |  {format_currency(project_cost.structure_cost):>14}
  Instalación ({INSTALLATION_FACTOR*100:.0f}%)                         |  {format_currency(project_cost.installation_cost):>14}
  Contingencia ({CONTINGENCY_FACTOR*100:.0f}%)                         |  {format_currency(project_cost.contingency):>14}
--------------------------------------------------------------------------------

================================================================================
  COSTO TOTAL PROYECTO                               |  {format_currency(project_cost.total):>14} MXN
================================================================================
  Presupuesto disponible                             |  {format_currency(project_cost.budget):>14} MXN
  Margen                                             |  {format_currency(project_cost.margin):>14} MXN
  Porcentaje de margen                               |  {project_cost.margin_percent:>13.1f}%
================================================================================

  ESTADO: [{status_indicator}] {status}

================================================================================

MÉTRICAS CLAVE:
--------------------------------------------------------------------------------
  Costo promedio por m²:         {format_currency(project_cost.total / total_area if total_area > 0 else 0)}
  Costo promedio por panel:      {format_currency(project_cost.total / total_panels if total_panels > 0 else 0)}
  Distribución óptima:           {flat.quantity/total_panels*100:.0f}% planos / {single.quantity/total_panels*100:.0f}% curvos / {double.quantity/total_panels*100:.0f}% dobles

================================================================================
"""

    return report


def generate_json_breakdown(project_cost, breakdowns):
    """
    Genera un JSON con el desglose de costos.

    Args:
        project_cost (ProjectCost): Costos del proyecto
        breakdowns (dict): Desglose por tipo

    Returns:
        str: JSON formateado
    """
    data = {
        "timestamp": "2025-12-27",
        "project": "Cubierta Museo Orgánica",
        "currency": "MXN",
        "panels": {
            "flat": {
                "quantity": breakdowns["flat"].quantity,
                "area_m2": round(breakdowns["flat"].total_area, 2),
                "cost_per_m2": breakdowns["flat"].cost_per_m2,
                "subtotal": round(breakdowns["flat"].subtotal, 2)
            },
            "single_curve": {
                "quantity": breakdowns["single_curve"].quantity,
                "area_m2": round(breakdowns["single_curve"].total_area, 2),
                "cost_per_m2": breakdowns["single_curve"].cost_per_m2,
                "subtotal": round(breakdowns["single_curve"].subtotal, 2)
            },
            "double_curve": {
                "quantity": breakdowns["double_curve"].quantity,
                "area_m2": round(breakdowns["double_curve"].total_area, 2),
                "cost_per_m2": breakdowns["double_curve"].cost_per_m2,
                "subtotal": round(breakdowns["double_curve"].subtotal, 2)
            }
        },
        "additional_costs": {
            "panels_subtotal": round(project_cost.panels_cost, 2),
            "structure": round(project_cost.structure_cost, 2),
            "installation": round(project_cost.installation_cost, 2),
            "contingency": round(project_cost.contingency, 2)
        },
        "summary": {
            "total_cost": round(project_cost.total, 2),
            "budget": round(project_cost.budget, 2),
            "margin": round(project_cost.margin, 2),
            "margin_percent": round(project_cost.margin_percent, 1),
            "is_within_budget": project_cost.is_within_budget
        }
    }

    return json.dumps(data, indent=2)


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

# Verificar inputs con valores por defecto
if 'flat_panels' not in dir():
    flat_panels = []
if 'single_curve' not in dir():
    single_curve = []
if 'double_curve' not in dir():
    double_curve = []
if 'budget' not in dir() or budget is None:
    budget = DEFAULT_BUDGET

# Calcular costos
project_cost, breakdowns = calculate_project_cost(
    flat_panels,
    single_curve,
    double_curve,
    budget
)

# Generar reportes
report = generate_cost_report(project_cost, breakdowns)
breakdown_json = generate_json_breakdown(project_cost, breakdowns)

# Imprimir reporte en consola
print(report)

# Preparar outputs para Grasshopper
total_cost = project_cost.total
is_within_budget = project_cost.is_within_budget

# Outputs estándar de Grasshopper (a, b, c, d)
a = report
b = total_cost
c = is_within_budget
d = breakdown_json
