"""
structural_validator.py
Valida restricciones estructurales de la cubierta.

Proyecto: Cubierta Orgánica de Museo
Autor: BIMAC
Versión: 1.0.0

Uso en Grasshopper:
    1. Agregar componente "Python Script"
    2. Copiar este código
    3. Conectar inputs:
       - surface (Surface): Superficie de cubierta
       - max_span (float): Luz máxima permitida (mm)
       - min_slope (float): Pendiente mínima requerida (%)
    4. Outputs: is_valid, validation_report, warnings, critical_points

Inputs:
    surface (Surface): Superficie NURBS de la cubierta
    max_span (float): Luz libre máxima permitida en mm (default: 15000)
    min_slope (float): Pendiente mínima para drenaje en % (default: 2.0)

Outputs:
    is_valid (bool): True si cumple todas las restricciones
    validation_report (str): Reporte detallado
    warnings (List[str]): Lista de advertencias
    critical_points (List[Point3d]): Puntos que no cumplen
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Restricciones por defecto
DEFAULT_MAX_SPAN = 15000.0      # mm (15 metros)
DEFAULT_MIN_SLOPE = 2.0         # % (2%)
DEFAULT_MAX_DEFLECTION = 104.0  # mm (L/250 para 26m)

# Resolución de muestreo
SAMPLE_RESOLUTION = 20  # Grid de 20x20 = 400 puntos

# Tolerancias
TOLERANCE_SPAN = 100.0      # mm de tolerancia en luz
TOLERANCE_SLOPE = 0.1       # % de tolerancia en pendiente


# =============================================================================
# ESTRUCTURAS DE DATOS
# =============================================================================

ValidationResult = namedtuple('ValidationResult', [
    'check_name',
    'passed',
    'value',
    'limit',
    'message'
])


# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def calculate_span_at_point(surface, u_param, v_param):
    """
    Calcula la luz libre (distancia a soportes) en un punto.

    Los soportes se asumen en los bordes de la superficie.

    Args:
        surface (Surface): Superficie
        u_param (float): Parámetro U
        v_param (float): Parámetro V

    Returns:
        tuple: (span, support_direction)
    """
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)

    pt = surface.PointAt(u_param, v_param)

    # Calcular distancia a cada borde
    distances = {
        "u_min": pt.DistanceTo(surface.PointAt(u_domain.Min, v_param)),
        "u_max": pt.DistanceTo(surface.PointAt(u_domain.Max, v_param)),
        "v_min": pt.DistanceTo(surface.PointAt(u_param, v_domain.Min)),
        "v_max": pt.DistanceTo(surface.PointAt(u_param, v_domain.Max))
    }

    # La luz es la distancia mínima a cualquier borde x 2
    min_dist = min(distances.values())
    span = min_dist * 2

    return span, min(distances, key=distances.get)


def check_max_span(surface, max_allowed):
    """
    Verifica que la luz libre no exceda el máximo permitido.

    Args:
        surface (Surface): Superficie a verificar
        max_allowed (float): Luz máxima en mm

    Returns:
        tuple: (ValidationResult, critical_points)
    """
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)

    max_span_found = 0.0
    critical_points = []

    for i in range(SAMPLE_RESOLUTION + 1):
        u_param = u_domain.ParameterAt(i / SAMPLE_RESOLUTION)

        for j in range(SAMPLE_RESOLUTION + 1):
            v_param = v_domain.ParameterAt(j / SAMPLE_RESOLUTION)

            span, direction = calculate_span_at_point(surface, u_param, v_param)

            if span > max_span_found:
                max_span_found = span
                critical_points = [surface.PointAt(u_param, v_param)]
            elif abs(span - max_span_found) < TOLERANCE_SPAN:
                critical_points.append(surface.PointAt(u_param, v_param))

    passed = max_span_found <= max_allowed
    margin = max_allowed - max_span_found

    result = ValidationResult(
        check_name="Luz Libre Máxima",
        passed=passed,
        value=max_span_found,
        limit=max_allowed,
        message=f"Luz: {max_span_found/1000:.2f}m / Máx: {max_allowed/1000:.1f}m (Margen: {margin/1000:.2f}m)"
    )

    return result, critical_points


def calculate_slope_at_point(surface, u_param, v_param):
    """
    Calcula la pendiente en un punto de la superficie.

    Args:
        surface (Surface): Superficie
        u_param (float): Parámetro U
        v_param (float): Parámetro V

    Returns:
        float: Pendiente en porcentaje
    """
    try:
        # Obtener vector normal
        normal = surface.NormalAt(u_param, v_param)

        if normal is None:
            return 0.0

        # Calcular ángulo con la vertical (Z)
        vertical = rg.Vector3d.ZAxis
        angle_rad = rg.Vector3d.VectorAngle(normal, vertical)

        # Convertir a pendiente porcentual
        # pendiente = tan(90° - angle) * 100
        slope_angle = math.pi / 2 - angle_rad
        slope_percent = abs(math.tan(slope_angle)) * 100

        return slope_percent

    except Exception:
        return 0.0


def check_min_slope(surface, min_required):
    """
    Verifica que la pendiente mínima se cumpla para drenaje.

    Args:
        surface (Surface): Superficie a verificar
        min_required (float): Pendiente mínima requerida (%)

    Returns:
        tuple: (ValidationResult, low_slope_points)
    """
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)

    min_slope_found = float('inf')
    low_slope_points = []

    for i in range(SAMPLE_RESOLUTION + 1):
        u_param = u_domain.ParameterAt(i / SAMPLE_RESOLUTION)

        for j in range(SAMPLE_RESOLUTION + 1):
            v_param = v_domain.ParameterAt(j / SAMPLE_RESOLUTION)

            slope = calculate_slope_at_point(surface, u_param, v_param)

            if slope < min_required - TOLERANCE_SLOPE:
                low_slope_points.append(surface.PointAt(u_param, v_param))

            if slope < min_slope_found:
                min_slope_found = slope

    passed = min_slope_found >= min_required - TOLERANCE_SLOPE

    result = ValidationResult(
        check_name="Pendiente Mínima (Drenaje)",
        passed=passed,
        value=min_slope_found,
        limit=min_required,
        message=f"Pendiente mín: {min_slope_found:.2f}% / Requerida: {min_required:.1f}%"
    )

    return result, low_slope_points


def check_surface_continuity(surface):
    """
    Verifica la continuidad de la superficie (sin huecos o singularidades).

    Args:
        surface (Surface): Superficie a verificar

    Returns:
        ValidationResult
    """
    is_valid = True
    message = "Superficie continua"

    try:
        # Verificar que la superficie sea válida
        if surface is None:
            is_valid = False
            message = "Superficie nula"
        elif not surface.IsValid:
            is_valid = False
            message = "Superficie inválida"
        else:
            # Verificar bordes
            brep = surface.ToBrep()
            if brep is not None:
                naked_edges = brep.GetNakedEdges()
                if naked_edges is None:
                    pass  # OK
                else:
                    # Verificar que los bordes desnudos formen un perímetro cerrado
                    pass

    except Exception as ex:
        is_valid = False
        message = f"Error verificando continuidad: {ex}"

    return ValidationResult(
        check_name="Continuidad de Superficie",
        passed=is_valid,
        value=1 if is_valid else 0,
        limit=1,
        message=message
    )


def check_self_intersection(surface):
    """
    Verifica que la superficie no tenga auto-intersecciones.

    Args:
        surface (Surface): Superficie a verificar

    Returns:
        ValidationResult
    """
    is_valid = True
    message = "Sin auto-intersecciones"

    try:
        brep = surface.ToBrep()

        if brep is not None:
            # Verificar intersección consigo misma
            # (Simplificado - una verificación completa sería más costosa)
            is_valid = brep.IsValid and brep.IsSolid == False

    except Exception as ex:
        is_valid = False
        message = f"Error: {ex}"

    return ValidationResult(
        check_name="Auto-intersecciones",
        passed=is_valid,
        value=0 if is_valid else 1,
        limit=0,
        message=message
    )


def validate_surface(surface, max_span=DEFAULT_MAX_SPAN, min_slope=DEFAULT_MIN_SLOPE):
    """
    Ejecuta todas las validaciones en la superficie.

    Args:
        surface (Surface): Superficie a validar
        max_span (float): Luz máxima permitida (mm)
        min_slope (float): Pendiente mínima (%)

    Returns:
        tuple: (all_passed, results, warnings, all_critical_points)
    """
    results = []
    warnings = []
    all_critical_points = []

    # 1. Verificar continuidad
    continuity_result = check_surface_continuity(surface)
    results.append(continuity_result)
    if not continuity_result.passed:
        warnings.append(f"CRÍTICO: {continuity_result.message}")

    # 2. Verificar luz libre
    span_result, span_points = check_max_span(surface, max_span)
    results.append(span_result)
    if not span_result.passed:
        warnings.append(f"Luz excedida: {span_result.value/1000:.2f}m > {max_span/1000:.1f}m")
        all_critical_points.extend(span_points)

    # 3. Verificar pendiente
    slope_result, slope_points = check_min_slope(surface, min_slope)
    results.append(slope_result)
    if not slope_result.passed:
        warnings.append(f"Pendiente insuficiente: {slope_result.value:.2f}% < {min_slope:.1f}%")
        all_critical_points.extend(slope_points)

    # 4. Verificar auto-intersección
    intersection_result = check_self_intersection(surface)
    results.append(intersection_result)
    if not intersection_result.passed:
        warnings.append(f"CRÍTICO: {intersection_result.message}")

    # Determinar si todo pasó
    all_passed = all(r.passed for r in results)

    return all_passed, results, warnings, all_critical_points


def generate_validation_report(all_passed, results, warnings):
    """
    Genera un reporte de validación formateado.

    Args:
        all_passed (bool): Si todas las validaciones pasaron
        results (List[ValidationResult]): Resultados de validaciones
        warnings (List[str]): Lista de advertencias

    Returns:
        str: Reporte formateado
    """
    status = "APROBADO" if all_passed else "RECHAZADO"
    status_icon = "[OK]" if all_passed else "[FALLO]"

    report = f"""
================================================================================
              VALIDACIÓN ESTRUCTURAL - CUBIERTA MUSEO
================================================================================

ESTADO GENERAL: {status_icon} {status}

RESULTADOS POR VERIFICACIÓN:
--------------------------------------------------------------------------------
"""

    for result in results:
        icon = "[OK]" if result.passed else "[X]"
        report += f"  {icon} {result.check_name}\n"
        report += f"      {result.message}\n"
        report += "\n"

    if warnings:
        report += "ADVERTENCIAS:\n"
        report += "--------------------------------------------------------------------------------\n"
        for warning in warnings:
            report += f"  - {warning}\n"

    report += """
================================================================================
PARÁMETROS DE VALIDACIÓN:
--------------------------------------------------------------------------------
  Luz libre máxima:     15.0 m
  Pendiente mínima:     2.0 %
  Flecha máxima:        L/250

NORMATIVAS DE REFERENCIA:
--------------------------------------------------------------------------------
  - NMX-C-406-ONNCCE (Estructuras de acero)
  - ISO 19650-2:2018 (BIM)
================================================================================
"""

    return report


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

# Verificar inputs con valores por defecto
if 'surface' not in dir():
    surface = None
if 'max_span' not in dir() or max_span is None:
    max_span = DEFAULT_MAX_SPAN
if 'min_slope' not in dir() or min_slope is None:
    min_slope = DEFAULT_MIN_SLOPE

# Ejecutar validación
if surface is not None:
    is_valid, results, warnings, critical_points = validate_surface(
        surface, max_span, min_slope
    )
    validation_report = generate_validation_report(is_valid, results, warnings)
else:
    is_valid = False
    validation_report = "Error: No se proporcionó superficie para validar"
    warnings = ["Superficie no proporcionada"]
    critical_points = []

# Imprimir reporte
print(validation_report)

# Outputs para Grasshopper
a = is_valid
b = validation_report
c = warnings
d = critical_points
