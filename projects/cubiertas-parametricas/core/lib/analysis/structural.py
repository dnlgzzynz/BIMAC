"""
Structural Validator

Validación de restricciones estructurales para cubiertas paramétricas.
"""

from collections import namedtuple

try:
    import Rhino.Geometry as rg
    import math
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False

# Estructuras de resultado
ValidationResult = namedtuple('ValidationResult', [
    'check_name',
    'passed',
    'value',
    'limit',
    'message'
])


class StructuralValidator:
    """
    Validador de restricciones estructurales.

    Verifica que una superficie cumpla con las restricciones
    estructurales definidas para el tipo de cubierta.

    Validaciones:
        - Luz libre máxima
        - Pendiente mínima (drenaje)
        - Continuidad de superficie
        - Curvatura máxima

    Example:
        >>> validator = StructuralValidator(max_span=15000, min_slope=2.0)
        >>> results = validator.validate(surface)
        >>> if results["all_passed"]:
        ...     print("Superficie válida")
    """

    # Configuración por tipo de cubierta
    DEFAULTS_BY_TYPE = {
        "organic": {
            "max_span": 15000,      # mm
            "min_slope": 2.0,       # %
            "max_deflection": 250,  # L/X
        },
        "tensile": {
            "max_span": 30000,
            "min_slope": 5.0,
            "max_deflection": 50,
        },
        "gridshell": {
            "max_span": 25000,
            "min_slope": 3.0,
            "max_deflection": 200,
        },
        "folded": {
            "max_span": 20000,
            "min_slope": 1.5,
            "max_deflection": 300,
        },
        "shell": {
            "max_span": 40000,
            "min_slope": 0,
            "max_deflection": 300,
        },
    }

    def __init__(self, max_span=None, min_slope=None, surface_type="organic",
                 sample_resolution=20):
        """
        Inicializa el validador.

        Args:
            max_span: Luz libre máxima en mm
            min_slope: Pendiente mínima en %
            surface_type: Tipo de superficie para defaults
            sample_resolution: Resolución de muestreo
        """
        defaults = self.DEFAULTS_BY_TYPE.get(surface_type, self.DEFAULTS_BY_TYPE["organic"])

        self.max_span = max_span or defaults["max_span"]
        self.min_slope = min_slope or defaults["min_slope"]
        self.sample_resolution = sample_resolution

    def validate(self, surface):
        """
        Ejecuta todas las validaciones en la superficie.

        Args:
            surface: Superficie a validar

        Returns:
            dict: Resultados de validación
                - all_passed: True si todas pasaron
                - results: Lista de ValidationResult
                - warnings: Lista de advertencias
                - critical_points: Puntos problemáticos
        """
        results = []
        warnings = []
        critical_points = []

        if surface is None:
            return {
                "all_passed": False,
                "results": [ValidationResult(
                    "Superficie", False, 0, 0, "Superficie no proporcionada"
                )],
                "warnings": ["Superficie nula"],
                "critical_points": [],
            }

        # 1. Validar luz libre
        span_result, span_points = self._check_max_span(surface)
        results.append(span_result)
        if not span_result.passed:
            warnings.append(f"Luz libre excedida: {span_result.value/1000:.2f}m > {self.max_span/1000:.1f}m")
            critical_points.extend(span_points)

        # 2. Validar pendiente mínima
        slope_result, slope_points = self._check_min_slope(surface)
        results.append(slope_result)
        if not slope_result.passed:
            warnings.append(f"Pendiente insuficiente: {slope_result.value:.2f}% < {self.min_slope:.1f}%")
            critical_points.extend(slope_points)

        # 3. Validar continuidad
        continuity_result = self._check_continuity(surface)
        results.append(continuity_result)
        if not continuity_result.passed:
            warnings.append(f"Problema de continuidad: {continuity_result.message}")

        # Resultado global
        all_passed = all(r.passed for r in results)

        return {
            "all_passed": all_passed,
            "results": results,
            "warnings": warnings,
            "critical_points": critical_points,
        }

    def _check_max_span(self, surface):
        """
        Verifica que la luz libre no exceda el máximo.

        Args:
            surface: Superficie a verificar

        Returns:
            tuple: (ValidationResult, lista de puntos críticos)
        """
        if not RHINO_AVAILABLE:
            return ValidationResult("Luz Libre", False, 0, self.max_span, "Rhino no disponible"), []

        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)

        max_span_found = 0
        critical_points = []

        # Muestrear superficie
        for i in range(self.sample_resolution + 1):
            u = u_domain.ParameterAt(i / self.sample_resolution)

            for j in range(self.sample_resolution + 1):
                v = v_domain.ParameterAt(j / self.sample_resolution)

                pt = surface.PointAt(u, v)

                # Distancia mínima a bordes
                distances = [
                    pt.DistanceTo(surface.PointAt(u_domain.Min, v)),
                    pt.DistanceTo(surface.PointAt(u_domain.Max, v)),
                    pt.DistanceTo(surface.PointAt(u, v_domain.Min)),
                    pt.DistanceTo(surface.PointAt(u, v_domain.Max)),
                ]

                min_dist = min(distances)
                span = min_dist * 2  # Luz libre = 2x distancia al borde

                if span > max_span_found:
                    max_span_found = span
                    critical_points = [pt]

        passed = max_span_found <= self.max_span

        result = ValidationResult(
            check_name="Luz Libre Máxima",
            passed=passed,
            value=max_span_found,
            limit=self.max_span,
            message=f"Luz: {max_span_found/1000:.2f}m / Máx: {self.max_span/1000:.1f}m"
        )

        return result, critical_points if not passed else []

    def _check_min_slope(self, surface):
        """
        Verifica que la pendiente mínima se cumpla.

        Args:
            surface: Superficie a verificar

        Returns:
            tuple: (ValidationResult, lista de puntos con pendiente baja)
        """
        if not RHINO_AVAILABLE:
            return ValidationResult("Pendiente", False, 0, self.min_slope, "Rhino no disponible"), []

        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)

        min_slope_found = float('inf')
        low_slope_points = []

        for i in range(self.sample_resolution + 1):
            u = u_domain.ParameterAt(i / self.sample_resolution)

            for j in range(self.sample_resolution + 1):
                v = v_domain.ParameterAt(j / self.sample_resolution)

                # Obtener normal
                normal = surface.NormalAt(u, v)
                if normal is None:
                    continue

                # Calcular pendiente
                vertical = rg.Vector3d.ZAxis
                angle = rg.Vector3d.VectorAngle(normal, vertical)

                # Convertir a pendiente porcentual
                if angle < math.pi / 2:
                    slope = math.tan(math.pi / 2 - angle) * 100
                else:
                    slope = 0

                if slope < self.min_slope:
                    low_slope_points.append(surface.PointAt(u, v))

                min_slope_found = min(min_slope_found, slope)

        passed = min_slope_found >= self.min_slope

        result = ValidationResult(
            check_name="Pendiente Mínima",
            passed=passed,
            value=min_slope_found,
            limit=self.min_slope,
            message=f"Pendiente mín: {min_slope_found:.2f}% / Requerida: {self.min_slope:.1f}%"
        )

        return result, low_slope_points if not passed else []

    def _check_continuity(self, surface):
        """
        Verifica la continuidad de la superficie.

        Args:
            surface: Superficie a verificar

        Returns:
            ValidationResult
        """
        passed = True
        message = "Superficie continua"

        try:
            if surface is None:
                passed = False
                message = "Superficie nula"
            elif not surface.IsValid:
                passed = False
                message = "Superficie inválida"
            else:
                # Verificar que se pueda evaluar en todo el dominio
                u_domain = surface.Domain(0)
                v_domain = surface.Domain(1)

                test_points = [
                    (u_domain.Min, v_domain.Min),
                    (u_domain.Max, v_domain.Min),
                    (u_domain.Max, v_domain.Max),
                    (u_domain.Min, v_domain.Max),
                    (u_domain.Mid, v_domain.Mid),
                ]

                for u, v in test_points:
                    pt = surface.PointAt(u, v)
                    if pt is None or not pt.IsValid:
                        passed = False
                        message = f"Punto inválido en ({u}, {v})"
                        break

        except Exception as ex:
            passed = False
            message = f"Error: {str(ex)}"

        return ValidationResult(
            check_name="Continuidad",
            passed=passed,
            value=1 if passed else 0,
            limit=1,
            message=message
        )

    def generate_report(self, validation_results):
        """
        Genera un reporte de validación.

        Args:
            validation_results: Resultados de validate()

        Returns:
            str: Reporte formateado
        """
        status = "APROBADO" if validation_results["all_passed"] else "RECHAZADO"

        report = f"""
================================================================================
              VALIDACIÓN ESTRUCTURAL - CUBIERTA PARAMÉTRICA
================================================================================

ESTADO GENERAL: [{status}]

RESULTADOS POR VERIFICACIÓN:
--------------------------------------------------------------------------------
"""
        for result in validation_results["results"]:
            icon = "[OK]" if result.passed else "[X]"
            report += f"  {icon} {result.check_name}\n"
            report += f"      {result.message}\n\n"

        if validation_results["warnings"]:
            report += "ADVERTENCIAS:\n"
            report += "-" * 80 + "\n"
            for warning in validation_results["warnings"]:
                report += f"  - {warning}\n"

        report += "=" * 80 + "\n"

        return report


# Función de conveniencia
def validate_structure(surface, max_span=None, min_slope=None, surface_type="organic"):
    """
    Valida restricciones estructurales de una superficie.

    Args:
        surface: Superficie a validar
        max_span: Luz máxima en mm
        min_slope: Pendiente mínima en %
        surface_type: Tipo de cubierta

    Returns:
        dict: Resultados de validación
    """
    validator = StructuralValidator(
        max_span=max_span,
        min_slope=min_slope,
        surface_type=surface_type
    )
    return validator.validate(surface)
