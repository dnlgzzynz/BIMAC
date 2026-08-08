"""
Structural Check - Muro Cortina Parametrico
Valida restricciones estructurales del sistema de muro cortina.

Inputs:
    mullions (List[ProfileData]): Datos de mullions
    transoms (List[ProfileData]): Datos de travesanos
    panels (List[PanelData]): Datos de paneles
    wind_load (float): Carga de viento (kPa)
    seismic_zone (str): Zona sismica (A/B/C/D)
    max_span (float): Luz maxima permitida (mm)

Outputs:
    is_valid (bool): Si pasa todas las validaciones
    results (List[dict]): Resultados de cada verificacion
    warnings (List[str]): Advertencias
    critical_elements (List): Elementos que fallan
"""

import math
from collections import namedtuple
from enum import Enum

# Resultados de verificacion
class CheckStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


CheckResult = namedtuple('CheckResult', [
    'name', 'status', 'actual_value', 'limit_value',
    'utilization', 'message', 'affected_elements'
])

ValidationResult = namedtuple('ValidationResult', [
    'is_valid', 'results', 'warnings', 'critical_elements',
    'overall_utilization', 'summary'
])


class StructuralProperties:
    """Propiedades estructurales de materiales."""

    # Aluminio 6063-T5
    ALUMINUM_6063 = {
        'E': 69000,          # MPa - Modulo de elasticidad
        'Fy': 110,           # MPa - Limite elastico
        'Fu': 150,           # MPa - Resistencia ultima
        'density': 2700,     # kg/m3
        'alpha': 23.6e-6     # 1/°C - Coef. expansion termica
    }

    # Aluminio 6061-T6
    ALUMINUM_6061 = {
        'E': 69000,
        'Fy': 240,
        'Fu': 290,
        'density': 2700,
        'alpha': 23.6e-6
    }

    # Acero inoxidable 304
    STAINLESS_304 = {
        'E': 193000,
        'Fy': 205,
        'Fu': 515,
        'density': 8000,
        'alpha': 17.3e-6
    }


class WindLoadCalculator:
    """Calcula cargas de viento segun normativa."""

    # Factores de forma para muro cortina
    PRESSURE_COEFFICIENTS = {
        'windward': 0.8,
        'leeward': -0.5,
        'side': -0.7,
        'corner': -1.2
    }

    def __init__(self, basic_wind_speed=None, exposure='B'):
        """
        Args:
            basic_wind_speed: Velocidad basica del viento (m/s)
            exposure: Categoria de exposicion (A/B/C/D)
        """
        self.basic_wind_speed = basic_wind_speed or 40
        self.exposure = exposure

    def calculate_design_pressure(self, height, zone='interior'):
        """
        Calcula presion de diseno en altura.

        Args:
            height: Altura sobre el terreno (m)
            zone: Zona del edificio

        Returns:
            float: Presion de diseno (kPa)
        """
        # Factor de exposicion por altura
        Kz = self._get_Kz(height)

        # Factor de rafaga
        Kzt = 1.0  # Topografia normal

        # Velocidad de presion
        qz = 0.613 * Kz * Kzt * (self.basic_wind_speed ** 2) / 1000  # kPa

        # Coeficiente de presion
        Cp = self.PRESSURE_COEFFICIENTS.get(zone, 0.8)

        # Factor de importancia
        I = 1.0

        # Presion de diseno
        p = qz * Cp * I

        return abs(p)

    def _get_Kz(self, height):
        """Factor de exposicion por altura."""
        exposure_params = {
            'A': (0.85, 7.0),    # Urbano denso
            'B': (1.0, 9.0),     # Suburbano
            'C': (1.2, 11.0),    # Campo abierto
            'D': (1.4, 14.0)     # Costa
        }

        alpha, zg = exposure_params.get(self.exposure, (1.0, 9.0))

        if height < 4.5:
            height = 4.5

        Kz = 2.01 * (height / zg) ** (2 / alpha)
        return min(Kz, 2.01)


class SeismicCalculator:
    """Calcula fuerzas sismicas en el muro cortina."""

    # Factores de zona sismica (Mexico)
    ZONE_FACTORS = {
        'A': 0.10,   # Baja sismicidad
        'B': 0.25,   # Media sismicidad
        'C': 0.40,   # Alta sismicidad
        'D': 0.50    # Muy alta sismicidad
    }

    def __init__(self, seismic_zone='C', importance_factor=1.0):
        self.zone = seismic_zone
        self.importance = importance_factor

    def calculate_drift_limit(self, story_height):
        """
        Calcula limite de deriva de entrepiso.

        Args:
            story_height: Altura de entrepiso (mm)

        Returns:
            float: Deriva maxima permitida (mm)
        """
        # Limite tipico: h/300 para muros cortina
        return story_height / 300

    def calculate_seismic_force(self, weight, height, building_height):
        """
        Calcula fuerza sismica en un nivel.

        Args:
            weight: Peso del muro cortina (kN)
            height: Altura del nivel (m)
            building_height: Altura total del edificio (m)

        Returns:
            float: Fuerza sismica (kN)
        """
        zone_factor = self.ZONE_FACTORS.get(self.zone, 0.4)

        # Factor de amplificacion por altura
        amplification = 1 + 2 * (height / building_height)

        # Coeficiente sismico
        Cs = zone_factor * self.importance * amplification

        return weight * Cs


class CurtainWallValidator:
    """Validador estructural del muro cortina."""

    def __init__(self):
        self.material = StructuralProperties.ALUMINUM_6063
        self.deflection_limit = 175  # L/175 para mullions
        self.safety_factor = 1.5

    def validate(self, mullions_data, transoms_data, panels_data,
                 wind_load=1.2, seismic_zone='C', max_span=4500):
        """
        Ejecuta todas las validaciones.

        Args:
            mullions_data: Lista de datos de mullions
            transoms_data: Lista de datos de travesanos
            panels_data: Lista de datos de paneles
            wind_load: Carga de viento (kPa)
            seismic_zone: Zona sismica
            max_span: Luz maxima (mm)

        Returns:
            ValidationResult
        """
        results = []
        warnings = []
        critical_elements = []

        # 1. Verificar luz maxima de mullions
        span_result = self._check_mullion_spans(
            mullions_data, max_span
        )
        results.append(span_result)
        if span_result.status == CheckStatus.FAIL:
            critical_elements.extend(span_result.affected_elements)

        # 2. Verificar deflexion de mullions
        deflection_result = self._check_mullion_deflection(
            mullions_data, wind_load
        )
        results.append(deflection_result)
        if deflection_result.status == CheckStatus.FAIL:
            critical_elements.extend(deflection_result.affected_elements)

        # 3. Verificar esfuerzos en mullions
        stress_result = self._check_mullion_stress(
            mullions_data, wind_load
        )
        results.append(stress_result)
        if stress_result.status == CheckStatus.FAIL:
            critical_elements.extend(stress_result.affected_elements)

        # 4. Verificar anclajes
        anchor_result = self._check_anchor_capacity(
            mullions_data, wind_load, seismic_zone
        )
        results.append(anchor_result)

        # 5. Verificar movimiento sismico
        seismic_result = self._check_seismic_drift(
            mullions_data, seismic_zone, max_span
        )
        results.append(seismic_result)

        # 6. Verificar peso de paneles
        panel_result = self._check_panel_weight(panels_data)
        results.append(panel_result)
        if panel_result.status == CheckStatus.WARNING:
            warnings.append(panel_result.message)

        # 7. Verificar expansion termica
        thermal_result = self._check_thermal_movement(
            mullions_data, transoms_data
        )
        results.append(thermal_result)
        if thermal_result.status == CheckStatus.WARNING:
            warnings.append(thermal_result.message)

        # Calcular resultado global
        is_valid = all(r.status != CheckStatus.FAIL for r in results)

        # Utilizacion maxima
        utilizations = [r.utilization for r in results if r.utilization]
        max_utilization = max(utilizations) if utilizations else 0

        # Generar resumen
        summary = self._generate_summary(results, is_valid)

        return ValidationResult(
            is_valid=is_valid,
            results=results,
            warnings=warnings,
            critical_elements=list(set(critical_elements)),
            overall_utilization=max_utilization,
            summary=summary
        )

    def _check_mullion_spans(self, mullions_data, max_span):
        """Verifica luz maxima de mullions."""
        max_span_m = max_span / 1000.0

        failed_elements = []
        max_found = 0

        for i, mullion in enumerate(mullions_data):
            length = mullion.length if hasattr(mullion, 'length') else 0
            if length > max_span_m:
                failed_elements.append(i)
            max_found = max(max_found, length)

        utilization = (max_found / max_span_m) * 100 if max_span_m > 0 else 0

        if failed_elements:
            status = CheckStatus.FAIL
            message = f"Luz excedida en {len(failed_elements)} mullions"
        elif utilization > 90:
            status = CheckStatus.WARNING
            message = f"Luz cercana al limite ({utilization:.1f}%)"
        else:
            status = CheckStatus.PASS
            message = "Luces dentro del limite"

        return CheckResult(
            name="Luz maxima de mullions",
            status=status,
            actual_value=max_found * 1000,
            limit_value=max_span,
            utilization=utilization,
            message=message,
            affected_elements=failed_elements
        )

    def _check_mullion_deflection(self, mullions_data, wind_load):
        """Verifica deflexion de mullions bajo carga de viento."""
        E = self.material['E'] * 1e6  # Pa

        max_utilization = 0
        failed_elements = []

        for i, mullion in enumerate(mullions_data):
            length = mullion.length if hasattr(mullion, 'length') else 3.6
            width = 0.065  # 65mm asumido si no hay dato

            # Momento de inercia aproximado (seccion rectangular hueca)
            depth = 0.150  # 150mm asumido
            t = 0.003  # 3mm pared
            I = (width * depth**3 / 12) - ((width - 2*t) * (depth - 2*t)**3 / 12)

            # Carga distribuida
            tributary_width = 1.5  # m asumido
            w = wind_load * 1000 * tributary_width  # N/m

            # Deflexion maxima (viga simplemente apoyada)
            delta = (5 * w * length**4) / (384 * E * I)

            # Deflexion permitida
            delta_max = length / self.deflection_limit

            utilization = (delta / delta_max) * 100

            if utilization > max_utilization:
                max_utilization = utilization

            if utilization > 100:
                failed_elements.append(i)

        if failed_elements:
            status = CheckStatus.FAIL
            message = f"Deflexion excedida en {len(failed_elements)} mullions"
        elif max_utilization > 80:
            status = CheckStatus.WARNING
            message = f"Deflexion cercana al limite ({max_utilization:.1f}%)"
        else:
            status = CheckStatus.PASS
            message = "Deflexiones dentro del limite"

        return CheckResult(
            name="Deflexion de mullions",
            status=status,
            actual_value=max_utilization,
            limit_value=100,
            utilization=max_utilization,
            message=message,
            affected_elements=failed_elements
        )

    def _check_mullion_stress(self, mullions_data, wind_load):
        """Verifica esfuerzos en mullions."""
        Fy = self.material['Fy']  # MPa
        allowable_stress = Fy / self.safety_factor

        max_utilization = 0
        failed_elements = []

        for i, mullion in enumerate(mullions_data):
            length = mullion.length if hasattr(mullion, 'length') else 3.6

            # Modulo de seccion aproximado
            width = 0.065
            depth = 0.150
            t = 0.003
            S = (width * depth**2 / 6) - ((width - 2*t) * (depth - 2*t)**2 / 6)

            # Momento maximo
            tributary_width = 1.5
            w = wind_load * 1000 * tributary_width
            M_max = w * length**2 / 8

            # Esfuerzo flexionante
            stress = (M_max / S) / 1e6  # MPa

            utilization = (stress / allowable_stress) * 100

            if utilization > max_utilization:
                max_utilization = utilization

            if utilization > 100:
                failed_elements.append(i)

        if failed_elements:
            status = CheckStatus.FAIL
            message = f"Esfuerzo excedido en {len(failed_elements)} mullions"
        elif max_utilization > 80:
            status = CheckStatus.WARNING
            message = f"Esfuerzo cercano al limite ({max_utilization:.1f}%)"
        else:
            status = CheckStatus.PASS
            message = "Esfuerzos dentro del limite"

        return CheckResult(
            name="Esfuerzo en mullions",
            status=status,
            actual_value=max_utilization,
            limit_value=100,
            utilization=max_utilization,
            message=message,
            affected_elements=failed_elements
        )

    def _check_anchor_capacity(self, mullions_data, wind_load, seismic_zone):
        """Verifica capacidad de anclajes."""
        # Fuerza por anclaje (simplificado)
        seismic_calc = SeismicCalculator(seismic_zone)

        max_force_per_anchor = 0
        for mullion in mullions_data:
            length = mullion.length if hasattr(mullion, 'length') else 3.6
            tributary_width = 1.5

            # Fuerza de viento
            wind_force = wind_load * length * tributary_width

            # Fuerza sismica (10% del peso como estimacion)
            weight = mullion.weight if hasattr(mullion, 'weight') else 50
            seismic_force = weight * 0.1 * seismic_calc.ZONE_FACTORS.get(seismic_zone, 0.4)

            total_force = max(wind_force, seismic_force)
            max_force_per_anchor = max(max_force_per_anchor, total_force)

        # Capacidad tipica de anclaje (kN)
        anchor_capacity = 15  # kN para anclaje tipico

        utilization = (max_force_per_anchor / anchor_capacity) * 100

        if utilization > 100:
            status = CheckStatus.FAIL
            message = "Capacidad de anclajes excedida"
        elif utilization > 75:
            status = CheckStatus.WARNING
            message = f"Anclajes al {utilization:.1f}% de capacidad"
        else:
            status = CheckStatus.PASS
            message = "Capacidad de anclajes OK"

        return CheckResult(
            name="Capacidad de anclajes",
            status=status,
            actual_value=max_force_per_anchor,
            limit_value=anchor_capacity,
            utilization=utilization,
            message=message,
            affected_elements=[]
        )

    def _check_seismic_drift(self, mullions_data, seismic_zone, story_height):
        """Verifica capacidad de movimiento sismico."""
        seismic_calc = SeismicCalculator(seismic_zone)
        drift_limit = seismic_calc.calculate_drift_limit(story_height)

        # Asumir capacidad de drift del sistema
        system_drift_capacity = story_height / 200  # Tipico para stick system

        utilization = (drift_limit / system_drift_capacity) * 100

        if utilization > 100:
            status = CheckStatus.FAIL
            message = "Sistema no acomoda deriva sismica requerida"
        elif utilization > 75:
            status = CheckStatus.WARNING
            message = f"Capacidad de deriva al {utilization:.1f}%"
        else:
            status = CheckStatus.PASS
            message = "Capacidad de deriva sismica OK"

        return CheckResult(
            name="Movimiento sismico",
            status=status,
            actual_value=drift_limit,
            limit_value=system_drift_capacity,
            utilization=utilization,
            message=message,
            affected_elements=[]
        )

    def _check_panel_weight(self, panels_data):
        """Verifica peso de paneles."""
        max_weight = 0
        heavy_panels = []

        for i, panel in enumerate(panels_data):
            area = panel.area if hasattr(panel, 'area') else 2.0
            # Peso tipico: 30 kg/m2 para DVH
            weight = area * 30

            if weight > 100:  # 100 kg limite por panel
                heavy_panels.append(i)

            max_weight = max(max_weight, weight)

        if max_weight > 150:
            status = CheckStatus.FAIL
            message = "Paneles demasiado pesados para manejo manual"
        elif max_weight > 100:
            status = CheckStatus.WARNING
            message = f"Paneles pesados ({max_weight:.0f} kg) - requiere equipo"
        else:
            status = CheckStatus.PASS
            message = "Peso de paneles adecuado"

        return CheckResult(
            name="Peso de paneles",
            status=status,
            actual_value=max_weight,
            limit_value=100,
            utilization=(max_weight / 100) * 100,
            message=message,
            affected_elements=heavy_panels
        )

    def _check_thermal_movement(self, mullions_data, transoms_data):
        """Verifica movimiento termico."""
        alpha = self.material['alpha']
        delta_T = 50  # Diferencia de temperatura (°C)

        max_movement = 0

        # Revisar mullions
        for mullion in mullions_data:
            length = mullion.length if hasattr(mullion, 'length') else 3.6
            movement = alpha * delta_T * length * 1000  # mm
            max_movement = max(max_movement, movement)

        # Revisar travesanos
        for transom in transoms_data:
            length = transom.length if hasattr(transom, 'length') else 1.5
            movement = alpha * delta_T * length * 1000
            max_movement = max(max_movement, movement)

        # Junta tipica de expansion: 10mm
        joint_capacity = 10  # mm

        utilization = (max_movement / joint_capacity) * 100

        if utilization > 100:
            status = CheckStatus.FAIL
            message = f"Movimiento termico ({max_movement:.1f}mm) excede juntas"
        elif utilization > 70:
            status = CheckStatus.WARNING
            message = f"Considerar juntas de expansion adicionales"
        else:
            status = CheckStatus.PASS
            message = "Movimiento termico acomodado"

        return CheckResult(
            name="Movimiento termico",
            status=status,
            actual_value=max_movement,
            limit_value=joint_capacity,
            utilization=utilization,
            message=message,
            affected_elements=[]
        )

    def _generate_summary(self, results, is_valid):
        """Genera resumen de validacion."""
        passed = sum(1 for r in results if r.status == CheckStatus.PASS)
        warnings = sum(1 for r in results if r.status == CheckStatus.WARNING)
        failed = sum(1 for r in results if r.status == CheckStatus.FAIL)

        return {
            'status': 'APROBADO' if is_valid else 'RECHAZADO',
            'total_checks': len(results),
            'passed': passed,
            'warnings': warnings,
            'failed': failed,
            'critical_checks': [r.name for r in results if r.status == CheckStatus.FAIL]
        }


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    validator = CurtainWallValidator()

    result = validator.validate(
        mullions_data=profiles_data if 'profiles_data' in dir() else [],
        transoms_data=[],
        panels_data=panel_data if 'panel_data' in dir() else [],
        wind_load=wind_load if 'wind_load' in dir() else 1.2,
        seismic_zone=seismic_zone if 'seismic_zone' in dir() else 'C',
        max_span=max_span if 'max_span' in dir() else 4500
    )

    # Salidas para Grasshopper
    is_valid = result.is_valid
    check_results = result.results
    warnings = result.warnings
    critical_elements = result.critical_elements
    summary = result.summary
