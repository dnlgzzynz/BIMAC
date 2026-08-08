"""
curvature_analyzer.py
Analiza curvatura gaussiana de superficies para clasificación de paneles.

Proyecto: Cubierta Orgánica de Museo
Autor: BIMAC
Versión: 1.0.0

Uso en Grasshopper:
    1. Agregar componente "Python Script"
    2. Copiar este código
    3. Conectar inputs: panels (List[Brep])
    4. Outputs: flat_panels, single_curve, double_curve, panel_types, curvature_values

Inputs:
    panels (List[Brep]): Lista de paneles (Breps) a analizar

Outputs:
    flat_panels (List[Brep]): Paneles clasificados como planos
    single_curve (List[Brep]): Paneles con curvatura simple
    double_curve (List[Brep]): Paneles con doble curvatura
    panel_types (List[str]): Tipo asignado a cada panel
    curvature_values (List[float]): Valor de curvatura gaussiana
"""

import Rhino.Geometry as rg
from collections import namedtuple

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Umbrales de curvatura gaussiana para clasificación
# Valores calibrados para paneles de policarbonato termoformable
THRESHOLD_FLAT = 0.0001      # Debajo de este valor = plano
THRESHOLD_SINGLE = 0.001     # Entre FLAT y SINGLE = curvatura simple
                             # Por encima de SINGLE = doble curvatura

# Número de puntos de muestreo para evaluar curvatura
SAMPLE_POINTS = 5  # Grid de 5x5 = 25 puntos por panel


# =============================================================================
# CLASES Y ESTRUCTURAS
# =============================================================================

PanelAnalysis = namedtuple('PanelAnalysis', [
    'panel',
    'panel_type',
    'curvature',
    'sample_points'
])


# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def get_surface_from_brep(brep):
    """
    Extrae la superficie principal de un Brep.

    Args:
        brep (Brep): Brep del panel

    Returns:
        Surface: Primera cara del Brep o None si no es válido
    """
    if brep is None:
        return None

    if not isinstance(brep, rg.Brep):
        return None

    if brep.Faces.Count == 0:
        return None

    return brep.Faces[0]


def calculate_gaussian_curvature_at_point(surface, u_param, v_param):
    """
    Calcula la curvatura gaussiana en un punto específico de la superficie.

    La curvatura gaussiana es el producto de las curvaturas principales:
    K = k1 * k2

    Donde:
    - K < 0: Punto de silla (curvatura doble anticlástica)
    - K = 0: Curvatura simple (cilíndrica o plana)
    - K > 0: Curvatura doble sinclástica (domo)

    Args:
        surface (Surface): Superficie a evaluar
        u_param (float): Parámetro U
        v_param (float): Parámetro V

    Returns:
        float: Valor de curvatura gaussiana
    """
    try:
        curvature = surface.CurvatureAt(u_param, v_param)

        if curvature is None:
            return 0.0

        return curvature.Gaussian
    except Exception:
        return 0.0


def sample_curvature_across_surface(surface, sample_count=SAMPLE_POINTS):
    """
    Muestrea la curvatura gaussiana en múltiples puntos de la superficie.

    Args:
        surface (Surface): Superficie a evaluar
        sample_count (int): Número de muestras por dirección

    Returns:
        tuple: (max_abs_curvature, mean_curvature, sample_values)
    """
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)

    curvature_values = []

    for i in range(sample_count):
        u_param = u_domain.ParameterAt(i / (sample_count - 1))

        for j in range(sample_count):
            v_param = v_domain.ParameterAt(j / (sample_count - 1))

            k = calculate_gaussian_curvature_at_point(surface, u_param, v_param)
            curvature_values.append(k)

    if not curvature_values:
        return 0.0, 0.0, []

    # Usar valor absoluto máximo como indicador principal
    max_abs = max(abs(k) for k in curvature_values)
    mean_val = sum(curvature_values) / len(curvature_values)

    return max_abs, mean_val, curvature_values


def classify_panel_by_curvature(max_curvature):
    """
    Clasifica el panel según su curvatura máxima.

    Args:
        max_curvature (float): Curvatura gaussiana máxima (valor absoluto)

    Returns:
        str: Tipo de panel ('flat', 'single_curve', 'double_curve')
    """
    if max_curvature < THRESHOLD_FLAT:
        return "flat"
    elif max_curvature < THRESHOLD_SINGLE:
        return "single_curve"
    else:
        return "double_curve"


def analyze_panel(panel):
    """
    Realiza análisis completo de curvatura de un panel.

    Args:
        panel (Brep): Panel a analizar

    Returns:
        PanelAnalysis: Resultado del análisis
    """
    surface = get_surface_from_brep(panel)

    if surface is None:
        return PanelAnalysis(
            panel=panel,
            panel_type="invalid",
            curvature=0.0,
            sample_points=[]
        )

    max_curv, mean_curv, samples = sample_curvature_across_surface(surface)
    panel_type = classify_panel_by_curvature(max_curv)

    return PanelAnalysis(
        panel=panel,
        panel_type=panel_type,
        curvature=max_curv,
        sample_points=samples
    )


def analyze_all_panels(panels):
    """
    Analiza y clasifica todos los paneles.

    Args:
        panels (List[Brep]): Lista de paneles

    Returns:
        dict: Resultados organizados por tipo
    """
    results = {
        "flat": [],
        "single_curve": [],
        "double_curve": [],
        "invalid": [],
        "types": [],
        "curvatures": [],
        "analyses": []
    }

    if panels is None:
        return results

    for panel in panels:
        analysis = analyze_panel(panel)
        results["analyses"].append(analysis)
        results["types"].append(analysis.panel_type)
        results["curvatures"].append(analysis.curvature)

        if analysis.panel_type == "flat":
            results["flat"].append(panel)
        elif analysis.panel_type == "single_curve":
            results["single_curve"].append(panel)
        elif analysis.panel_type == "double_curve":
            results["double_curve"].append(panel)
        else:
            results["invalid"].append(panel)

    return results


def generate_report(results):
    """
    Genera reporte de análisis de curvatura.

    Args:
        results (dict): Resultados del análisis

    Returns:
        str: Reporte formateado
    """
    total = len(results["types"])

    if total == 0:
        return "No hay paneles para analizar"

    flat_count = len(results["flat"])
    single_count = len(results["single_curve"])
    double_count = len(results["double_curve"])
    invalid_count = len(results["invalid"])

    report = f"""
================================================================================
                    ANÁLISIS DE CURVATURA DE PANELES
================================================================================

RESUMEN:
--------------------------------------------------------------------------------
  Total de paneles:        {total:5d}
  Paneles planos:          {flat_count:5d}  ({flat_count/total*100:5.1f}%)
  Curvatura simple:        {single_count:5d}  ({single_count/total*100:5.1f}%)
  Doble curvatura:         {double_count:5d}  ({double_count/total*100:5.1f}%)
  Inválidos:               {invalid_count:5d}  ({invalid_count/total*100:5.1f}%)

UMBRALES UTILIZADOS:
--------------------------------------------------------------------------------
  Plano:           K < {THRESHOLD_FLAT}
  Curvatura simple: {THRESHOLD_FLAT} <= K < {THRESHOLD_SINGLE}
  Doble curvatura:  K >= {THRESHOLD_SINGLE}

ESTADÍSTICAS DE CURVATURA:
--------------------------------------------------------------------------------
"""

    if results["curvatures"]:
        valid_curvatures = [k for k in results["curvatures"] if k > 0]
        if valid_curvatures:
            report += f"  Curvatura máxima:    {max(valid_curvatures):.6f}\n"
            report += f"  Curvatura mínima:    {min(valid_curvatures):.6f}\n"
            report += f"  Curvatura promedio:  {sum(valid_curvatures)/len(valid_curvatures):.6f}\n"

    report += "================================================================================\n"

    return report


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

# Verificar que existan inputs
if 'panels' not in dir():
    panels = []

# Ejecutar análisis
results = analyze_all_panels(panels)

# Generar reporte
report = generate_report(results)
print(report)

# Preparar outputs para Grasshopper
flat_panels = results["flat"]
single_curve = results["single_curve"]
double_curve = results["double_curve"]
panel_types = results["types"]
curvature_values = results["curvatures"]

# Outputs estándar de Grasshopper (a, b, c, d, e)
a = flat_panels
b = single_curve
c = double_curve
d = panel_types
e = curvature_values
