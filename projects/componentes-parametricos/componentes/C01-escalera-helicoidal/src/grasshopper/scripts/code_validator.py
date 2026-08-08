"""
Code Validator - Escalera Helicoidal Parametrica
Valida cumplimiento de normativas (NTC-RCDF, IBC, OSHA).

Inputs:
    spiral_data (SpiralData): Datos de la espiral
    tread_data (List[TreadGeometry]): Datos de peldanos
    railing_data (dict): Datos del barandal
    code (str): Codigo normativo a aplicar
    use_type (str): Tipo de uso (residential, commercial, industrial)

Outputs:
    is_compliant (bool): Cumple normativa
    violations (List[str]): Lista de violaciones
    warnings (List[str]): Lista de advertencias
    report (dict): Reporte detallado
"""

import math
from collections import namedtuple

# Resultado de validacion
ValidationResult = namedtuple('ValidationResult', [
    'is_compliant', 'violations', 'warnings',
    'checks', 'score', 'report'
])

# Resultado de check individual
CheckResult = namedtuple('CheckResult', [
    'name', 'category', 'passed', 'value',
    'min_value', 'max_value', 'unit', 'message'
])


class BuildingCode:
    """Clase base para codigos de construccion."""

    def __init__(self, code_name, use_type='residential'):
        self.code_name = code_name
        self.use_type = use_type
        self.requirements = {}

    def get_requirement(self, param):
        """Obtiene requisito por nombre."""
        return self.requirements.get(param, None)

    def check_range(self, value, min_val, max_val, name, unit='mm'):
        """Verifica si valor esta en rango."""
        passed = True
        message = f"{name}: {value:.1f} {unit} - OK"

        if min_val is not None and value < min_val:
            passed = False
            message = f"{name}: {value:.1f} {unit} < {min_val} {unit} (minimo)"
        elif max_val is not None and value > max_val:
            passed = False
            message = f"{name}: {value:.1f} {unit} > {max_val} {unit} (maximo)"

        return CheckResult(
            name=name,
            category='geometry',
            passed=passed,
            value=value,
            min_value=min_val,
            max_value=max_val,
            unit=unit,
            message=message
        )


class NTC_RCDF(BuildingCode):
    """Normas Tecnicas Complementarias RCDF (Mexico)."""

    def __init__(self, use_type='residential'):
        super().__init__('NTC-RCDF', use_type)

        # Requisitos por tipo de uso
        if use_type == 'residential':
            self.requirements = {
                'riser_max': 200,
                'riser_min': 140,
                'tread_min_center': 200,  # En linea de paso
                'tread_min_outer': 250,
                'width_min': 900,
                'headroom_min': 2050,
                'handrail_height_min': 900,
                'handrail_height_max': 1070,
                'baluster_spacing_max': 100,
                'landing_every_steps': 16,
                'diameter_min': 1400,
                'walkline_radius': 300,  # Desde borde interior
            }
        elif use_type == 'commercial':
            self.requirements = {
                'riser_max': 180,
                'riser_min': 140,
                'tread_min_center': 250,
                'tread_min_outer': 280,
                'width_min': 1200,
                'headroom_min': 2100,
                'handrail_height_min': 900,
                'handrail_height_max': 1100,
                'baluster_spacing_max': 100,
                'landing_every_steps': 12,
                'diameter_min': 1600,
                'walkline_radius': 300,
            }
        else:  # industrial
            self.requirements = {
                'riser_max': 220,
                'riser_min': 130,
                'tread_min_center': 180,
                'tread_min_outer': 220,
                'width_min': 750,
                'headroom_min': 2000,
                'handrail_height_min': 850,
                'handrail_height_max': 1100,
                'baluster_spacing_max': 150,
                'landing_every_steps': 20,
                'diameter_min': 1200,
                'walkline_radius': 250,
            }


class IBC(BuildingCode):
    """International Building Code."""

    def __init__(self, use_type='residential'):
        super().__init__('IBC', use_type)

        # Conversiones: 1 inch = 25.4 mm
        inch = 25.4

        if use_type == 'residential':
            self.requirements = {
                'riser_max': 7.75 * inch,      # 197 mm
                'riser_min': 4.0 * inch,       # 102 mm
                'tread_min_walkline': 11.0 * inch,  # 280 mm at walkline
                'walkline_radius': 12.0 * inch,     # 305 mm from narrow end
                'width_min': 26.0 * inch,      # 660 mm
                'headroom_min': 80.0 * inch,   # 2032 mm
                'handrail_height_min': 34.0 * inch,  # 864 mm
                'handrail_height_max': 38.0 * inch,  # 965 mm
                'baluster_spacing_max': 4.0 * inch,  # 102 mm
                'handrail_grip_min': 1.25 * inch,    # 32 mm
                'handrail_grip_max': 2.0 * inch,     # 51 mm
                'landing_every_steps': 16,
                'diameter_min': 60.0 * inch,   # 1524 mm
            }
        else:  # commercial/public
            self.requirements = {
                'riser_max': 7.0 * inch,       # 178 mm
                'riser_min': 4.0 * inch,       # 102 mm
                'tread_min_walkline': 11.0 * inch,  # 280 mm
                'walkline_radius': 12.0 * inch,     # 305 mm
                'width_min': 36.0 * inch,      # 914 mm
                'headroom_min': 80.0 * inch,   # 2032 mm
                'handrail_height_min': 34.0 * inch,
                'handrail_height_max': 38.0 * inch,
                'baluster_spacing_max': 4.0 * inch,
                'handrail_grip_min': 1.25 * inch,
                'handrail_grip_max': 2.0 * inch,
                'landing_every_steps': 12,
                'diameter_min': 60.0 * inch,
            }


class OSHA(BuildingCode):
    """OSHA Industrial Standards."""

    def __init__(self, use_type='industrial'):
        super().__init__('OSHA', 'industrial')

        inch = 25.4

        self.requirements = {
            'riser_max': 9.5 * inch,       # 241 mm
            'riser_min': 6.0 * inch,       # 152 mm
            'tread_min': 9.0 * inch,       # 229 mm
            'width_min': 22.0 * inch,      # 559 mm
            'headroom_min': 78.0 * inch,   # 1981 mm
            'handrail_height_min': 30.0 * inch,  # 762 mm
            'handrail_height_max': 38.0 * inch,  # 965 mm
            'baluster_spacing_max': 19.0 * inch, # 483 mm (midrail)
            'angle_max': 50,  # grados desde horizontal
            'angle_min': 30,  # grados
            'landing_every_steps': 12,
            'diameter_min': 22.0 * inch,  # 559 mm
        }


class SpiralStairValidator:
    """Validador de escaleras helicoidales."""

    CODE_CLASSES = {
        'ntc_rcdf': NTC_RCDF,
        'mexico_ntc': NTC_RCDF,
        'ibc': IBC,
        'osha': OSHA
    }

    def __init__(self, code='ntc_rcdf', use_type='residential'):
        self.code_name = code
        self.use_type = use_type

        code_class = self.CODE_CLASSES.get(code.lower(), NTC_RCDF)
        self.code = code_class(use_type)

    def validate(self, spiral_data, tread_data=None, railing_data=None):
        """
        Valida la escalera contra el codigo.

        Args:
            spiral_data: Datos de la espiral
            tread_data: Datos de peldanos (opcional)
            railing_data: Datos del barandal (opcional)

        Returns:
            ValidationResult
        """
        checks = []
        violations = []
        warnings = []

        stats = spiral_data.geometry_stats

        # === VALIDACIONES DE GEOMETRIA ===

        # 1. Altura de contrahuella
        riser = stats['actual_riser']
        check = self.code.check_range(
            riser,
            self.code.get_requirement('riser_min'),
            self.code.get_requirement('riser_max'),
            'Altura de contrahuella'
        )
        checks.append(check)
        if not check.passed:
            violations.append(check.message)

        # 2. Huella en linea de paso
        tread_walkline = stats.get('tread_at_walkline', 0)
        if tread_walkline == 0:
            # Calcular huella en linea de paso
            walkline_radius = self.code.get_requirement('walkline_radius')
            if walkline_radius is None:
                walkline_radius = 300

            inner_radius = stats['inner_diameter'] / 2
            walkline_r = inner_radius + walkline_radius
            rotation_rad = math.radians(stats['rotation_per_tread'])
            tread_walkline = walkline_r * rotation_rad

        min_tread = (self.code.get_requirement('tread_min_walkline') or
                     self.code.get_requirement('tread_min_center') or 200)

        check = self.code.check_range(
            tread_walkline,
            min_tread,
            None,
            'Huella en linea de paso'
        )
        checks.append(check)
        if not check.passed:
            violations.append(check.message)

        # 3. Diametro minimo
        diameter_min = self.code.get_requirement('diameter_min')
        if diameter_min:
            check = self.code.check_range(
                stats['outer_diameter'],
                diameter_min,
                None,
                'Diametro exterior'
            )
            checks.append(check)
            if not check.passed:
                violations.append(check.message)

        # 4. Ancho de escalera (clear width)
        clear_width = (stats['outer_diameter'] - stats['inner_diameter']) / 2
        width_min = self.code.get_requirement('width_min')
        if width_min:
            check = self.code.check_range(
                clear_width,
                width_min,
                None,
                'Ancho libre'
            )
            checks.append(check)
            if not check.passed:
                violations.append(check.message)

        # 5. Altura libre (headroom)
        # Calcular headroom (distancia vertical entre peldanos superpuestos)
        rotation = stats['total_rotation']
        if rotation > 360:
            # Hay superposicion
            overlap_treads = int((rotation - 360) / stats['rotation_per_tread'])
            headroom = stats['floor_to_floor'] - (overlap_treads * stats['actual_riser'])
        else:
            headroom = stats['floor_to_floor']

        headroom_min = self.code.get_requirement('headroom_min')
        if headroom_min:
            check = self.code.check_range(
                headroom,
                headroom_min,
                None,
                'Altura libre'
            )
            checks.append(check)
            if not check.passed:
                violations.append(check.message)

        # 6. Numero de peldanos sin descanso
        landing_every = self.code.get_requirement('landing_every_steps')
        if landing_every and stats['tread_count'] > landing_every:
            warnings.append(
                f"Se recomienda descanso cada {landing_every} peldanos. "
                f"Actual: {stats['tread_count']} peldanos"
            )

        # === VALIDACIONES DE BARANDAL ===

        if railing_data:
            # 7. Altura de pasamanos
            handrail_height = railing_data.get('handrail_height', 0)
            hr_min = self.code.get_requirement('handrail_height_min')
            hr_max = self.code.get_requirement('handrail_height_max')

            if hr_min or hr_max:
                check = self.code.check_range(
                    handrail_height,
                    hr_min,
                    hr_max,
                    'Altura de pasamanos'
                )
                checks.append(check)
                if not check.passed:
                    violations.append(check.message)

            # 8. Espaciamiento de balaustres
            baluster_spacing = railing_data.get('baluster_spacing', 0)
            spacing_max = self.code.get_requirement('baluster_spacing_max')

            if spacing_max and baluster_spacing > 0:
                check = self.code.check_range(
                    baluster_spacing,
                    None,
                    spacing_max,
                    'Espaciamiento de balaustres'
                )
                checks.append(check)
                if not check.passed:
                    violations.append(check.message)

            # 9. Diametro de pasamanos (grip)
            handrail_diameter = railing_data.get('handrail_diameter', 0)
            grip_min = self.code.get_requirement('handrail_grip_min')
            grip_max = self.code.get_requirement('handrail_grip_max')

            if grip_min or grip_max:
                check = self.code.check_range(
                    handrail_diameter,
                    grip_min,
                    grip_max,
                    'Diametro de pasamanos'
                )
                checks.append(check)
                if not check.passed:
                    warnings.append(check.message)  # Warning, no violation

        # === VALIDACIONES ADICIONALES ===

        # 10. Angulo de inclinacion (OSHA)
        if self.code_name.lower() == 'osha':
            # Calcular angulo
            rise = stats['floor_to_floor']
            run = stats['helix_length']
            angle = math.degrees(math.atan2(rise, run))

            angle_min = self.code.get_requirement('angle_min')
            angle_max = self.code.get_requirement('angle_max')

            if angle_min or angle_max:
                check = self.code.check_range(
                    angle,
                    angle_min,
                    angle_max,
                    'Angulo de inclinacion',
                    'grados'
                )
                checks.append(check)
                if not check.passed:
                    violations.append(check.message)

        # === CALCULAR RESULTADO ===

        passed_checks = sum(1 for c in checks if c.passed)
        total_checks = len(checks)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        is_compliant = len(violations) == 0

        # Generar reporte
        report = {
            'code': self.code_name,
            'use_type': self.use_type,
            'is_compliant': is_compliant,
            'score': score,
            'checks_passed': passed_checks,
            'checks_total': total_checks,
            'violations_count': len(violations),
            'warnings_count': len(warnings),
            'geometry': {
                'outer_diameter': stats['outer_diameter'],
                'inner_diameter': stats['inner_diameter'],
                'floor_to_floor': stats['floor_to_floor'],
                'tread_count': stats['tread_count'],
                'riser_height': stats['actual_riser'],
                'total_rotation': stats['total_rotation'],
            },
            'requirements_used': dict(self.code.requirements),
            'detailed_checks': [
                {
                    'name': c.name,
                    'passed': c.passed,
                    'value': c.value,
                    'limits': f"{c.min_value or '-'} - {c.max_value or '-'}",
                    'unit': c.unit,
                    'message': c.message
                }
                for c in checks
            ]
        }

        return ValidationResult(
            is_compliant=is_compliant,
            violations=violations,
            warnings=warnings,
            checks=checks,
            score=score,
            report=report
        )

    def get_recommendations(self, spiral_data):
        """
        Genera recomendaciones para cumplir normativa.

        Args:
            spiral_data: Datos de la espiral

        Returns:
            List[str]: Recomendaciones
        """
        recommendations = []
        stats = spiral_data.geometry_stats

        # Verificar contrahuella
        riser = stats['actual_riser']
        riser_max = self.code.get_requirement('riser_max') or 200

        if riser > riser_max:
            # Recomendar mas peldanos
            ideal_treads = math.ceil(stats['floor_to_floor'] / riser_max)
            recommendations.append(
                f"Aumentar numero de peldanos a {ideal_treads} para reducir "
                f"altura de contrahuella a {stats['floor_to_floor'] / ideal_treads:.0f} mm"
            )

        # Verificar huella
        walkline_radius = self.code.get_requirement('walkline_radius') or 300
        inner_radius = stats['inner_diameter'] / 2
        walkline_r = inner_radius + walkline_radius
        rotation_rad = math.radians(stats['rotation_per_tread'])
        tread_walkline = walkline_r * rotation_rad

        min_tread = self.code.get_requirement('tread_min_walkline') or 250

        if tread_walkline < min_tread:
            # Recomendar mas rotacion o mayor diametro
            needed_rotation = min_tread / walkline_r
            recommendations.append(
                f"Aumentar rotacion por peldano a {math.degrees(needed_rotation):.1f}° "
                f"o aumentar diametro exterior para lograr huella de {min_tread} mm"
            )

        # Verificar diametro
        diameter_min = self.code.get_requirement('diameter_min')
        if diameter_min and stats['outer_diameter'] < diameter_min:
            recommendations.append(
                f"Aumentar diametro exterior a minimo {diameter_min} mm"
            )

        return recommendations


class MultiCodeValidator:
    """Valida contra multiples codigos simultaneamente."""

    def __init__(self, codes=None, use_type='residential'):
        if codes is None:
            codes = ['ntc_rcdf', 'ibc']

        self.validators = {
            code: SpiralStairValidator(code, use_type)
            for code in codes
        }

    def validate_all(self, spiral_data, tread_data=None, railing_data=None):
        """
        Valida contra todos los codigos configurados.

        Returns:
            dict: Resultados por codigo
        """
        results = {}

        for code_name, validator in self.validators.items():
            results[code_name] = validator.validate(
                spiral_data, tread_data, railing_data
            )

        return results

    def get_summary(self, results):
        """Genera resumen de validacion multi-codigo."""
        summary = {
            'codes_checked': list(results.keys()),
            'all_compliant': all(r.is_compliant for r in results.values()),
            'by_code': {}
        }

        for code, result in results.items():
            summary['by_code'][code] = {
                'compliant': result.is_compliant,
                'score': result.score,
                'violations': len(result.violations),
                'warnings': len(result.warnings)
            }

        return summary


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    code = code if 'code' in dir() else 'ntc_rcdf'
    use_type = use_type if 'use_type' in dir() else 'residential'

    validator = SpiralStairValidator(code, use_type)

    result = validator.validate(
        spiral_data=spiral_data if 'spiral_data' in dir() else None,
        tread_data=tread_data if 'tread_data' in dir() else None,
        railing_data=railing_data if 'railing_data' in dir() else None
    )

    # Salidas para Grasshopper
    is_compliant = result.is_compliant
    violations = result.violations
    warnings = result.warnings
    score = result.score
    report = result.report

    # Recomendaciones si no cumple
    if not is_compliant:
        recommendations = validator.get_recommendations(
            spiral_data if 'spiral_data' in dir() else None
        )
