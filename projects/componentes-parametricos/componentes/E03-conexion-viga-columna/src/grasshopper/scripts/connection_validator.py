"""
Connection Validator - Conexion Viga-Columna Parametrica
Valida conexiones segun AISC 360, AISC 358 y AWS D1.1.

Inputs:
    connection_data (ConnectionData): Datos de la conexion
    demand_shear (float): Demanda de corte (kN)
    demand_moment (float): Demanda de momento (kN-m)
    code (str): Codigo de diseno

Outputs:
    is_valid (bool): Cumple todos los requisitos
    checks (List[dict]): Resultados de verificaciones
    dcr (float): Demand/Capacity Ratio maximo
    report (dict): Reporte detallado
"""

import math
from collections import namedtuple

# Resultado de validacion
ValidationResult = namedtuple('ValidationResult', [
    'is_valid', 'checks', 'dcr_max', 'warnings',
    'report', 'recommendations'
])

# Resultado de verificacion individual
CheckResult = namedtuple('CheckResult', [
    'name', 'category', 'passed', 'demand', 'capacity',
    'dcr', 'reference', 'message'
])


class AISCMaterialProperties:
    """Propiedades de materiales segun AISC."""

    MATERIALS = {
        'A36': {'Fy': 250, 'Fu': 400, 'E': 200000},
        'A572_Gr50': {'Fy': 345, 'Fu': 450, 'E': 200000},
        'A992': {'Fy': 345, 'Fu': 450, 'E': 200000},
        'A500_Gr_B': {'Fy': 290, 'Fu': 400, 'E': 200000},
    }

    BOLTS = {
        'A325': {'Fnt': 620, 'Fnv_N': 372, 'Fnv_X': 457},
        'A490': {'Fnt': 780, 'Fnv_N': 457, 'Fnv_X': 579},
    }

    WELDS = {
        'E70': {'Fexx': 482},
        'E80': {'Fexx': 551},
    }

    @classmethod
    def get_material(cls, name):
        return cls.MATERIALS.get(name, cls.MATERIALS['A992'])

    @classmethod
    def get_bolt(cls, grade):
        return cls.BOLTS.get(grade, cls.BOLTS['A325'])

    @classmethod
    def get_weld(cls, electrode):
        return cls.WELDS.get(electrode, cls.WELDS['E70'])


class BoltValidator:
    """Validador de tornillos segun AISC J3."""

    def __init__(self, diameter, grade, threads_included=True):
        self.diameter = diameter
        self.grade = grade
        self.threads_included = threads_included
        self.Ab = math.pi * (diameter / 2) ** 2  # mm2
        self.props = AISCMaterialProperties.get_bolt(grade)

    def check_shear(self, Vu, num_bolts, num_planes=1):
        """
        Verifica corte en tornillos (AISC J3.6).

        Args:
            Vu: Demanda de corte (kN)
            num_bolts: Numero de tornillos
            num_planes: Numero de planos de corte

        Returns:
            CheckResult
        """
        # Resistencia nominal
        if self.threads_included:
            Fnv = self.props['Fnv_N']
        else:
            Fnv = self.props['Fnv_X']

        phi = 0.75
        Rn = Fnv * self.Ab * num_planes / 1000  # kN por tornillo
        phi_Rn = phi * Rn * num_bolts  # Capacidad total

        dcr = Vu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Bolt Shear',
            category='bolts',
            passed=passed,
            demand=Vu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J3.6',
            message=f'Vu={Vu:.1f}kN <= φRn={phi_Rn:.1f}kN' if passed else f'FALLA: Vu={Vu:.1f}kN > φRn={phi_Rn:.1f}kN'
        )

    def check_tension(self, Tu, num_bolts):
        """
        Verifica tension en tornillos (AISC J3.6).

        Args:
            Tu: Demanda de tension (kN)
            num_bolts: Numero de tornillos

        Returns:
            CheckResult
        """
        Fnt = self.props['Fnt']
        phi = 0.75

        Rn = Fnt * self.Ab / 1000  # kN por tornillo
        phi_Rn = phi * Rn * num_bolts

        dcr = Tu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Bolt Tension',
            category='bolts',
            passed=passed,
            demand=Tu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J3.6',
            message=f'Tu={Tu:.1f}kN <= φRn={phi_Rn:.1f}kN' if passed else f'FALLA: Tu={Tu:.1f}kN > φRn={phi_Rn:.1f}kN'
        )

    def check_combined(self, Tu, Vu, num_bolts):
        """
        Verifica interaccion tension-corte (AISC J3.7).

        Returns:
            CheckResult
        """
        Fnt = self.props['Fnt']
        if self.threads_included:
            Fnv = self.props['Fnv_N']
        else:
            Fnv = self.props['Fnv_X']

        phi = 0.75

        # Esfuerzo de corte requerido
        frv = Vu * 1000 / (num_bolts * self.Ab)  # MPa

        # Resistencia a tension modificada
        Fnt_mod = 1.3 * Fnt - (Fnt / (phi * Fnv)) * frv
        Fnt_mod = min(Fnt_mod, Fnt)
        Fnt_mod = max(Fnt_mod, 0)

        # Capacidad a tension modificada
        Rn = Fnt_mod * self.Ab / 1000  # kN
        phi_Rn = phi * Rn * num_bolts

        Tu_per_bolt = Tu / num_bolts if num_bolts > 0 else Tu
        dcr = Tu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Bolt Combined T+V',
            category='bolts',
            passed=passed,
            demand=Tu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J3.7',
            message=f'Interaccion T-V: DCR={dcr:.2f}' if passed else f'FALLA: Interaccion T-V: DCR={dcr:.2f}'
        )

    def check_bearing(self, Vu, plate_thickness, edge_distance, spacing,
                       plate_Fu, num_bolts, deformation_permitted=True):
        """
        Verifica bearing y tearout (AISC J3.10).

        Returns:
            CheckResult
        """
        d = self.diameter
        phi = 0.75

        if deformation_permitted:
            # Con deformacion permitida
            Rn_bearing = 2.4 * d * plate_thickness * plate_Fu / 1000  # kN
            Rn_tearout = 1.2 * (edge_distance - d/2) * plate_thickness * plate_Fu / 1000
        else:
            # Sin deformacion
            Rn_bearing = 2.0 * d * plate_thickness * plate_Fu / 1000
            Rn_tearout = 1.0 * (edge_distance - d/2) * plate_thickness * plate_Fu / 1000

        Rn = min(Rn_bearing, Rn_tearout)
        phi_Rn = phi * Rn * num_bolts

        dcr = Vu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Bolt Bearing/Tearout',
            category='bolts',
            passed=passed,
            demand=Vu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J3.10',
            message=f'Bearing: DCR={dcr:.2f}' if passed else f'FALLA: Bearing: DCR={dcr:.2f}'
        )


class WeldValidator:
    """Validador de soldaduras segun AISC J2 y AWS D1.1."""

    def __init__(self, electrode='E70'):
        self.electrode = electrode
        self.props = AISCMaterialProperties.get_weld(electrode)

    def check_fillet_weld(self, force, weld_length, weld_size, angle=0):
        """
        Verifica soldadura de filete (AISC J2.4).

        Args:
            force: Fuerza en la soldadura (kN)
            weld_length: Longitud de soldadura (mm)
            weld_size: Tamano del filete (mm)
            angle: Angulo de carga (grados)

        Returns:
            CheckResult
        """
        Fexx = self.props['Fexx']
        phi = 0.75

        # Garganta efectiva
        a = 0.707 * weld_size

        # Factor direccional
        theta = math.radians(angle)
        directional_factor = 1.0 + 0.5 * math.sin(theta) ** 1.5

        # Resistencia
        Fnw = 0.60 * Fexx * directional_factor
        Rn = Fnw * a * weld_length / 1000  # kN
        phi_Rn = phi * Rn

        dcr = force / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Fillet Weld',
            category='welds',
            passed=passed,
            demand=force,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J2.4',
            message=f'Filete {weld_size}mm: DCR={dcr:.2f}' if passed else f'FALLA: Filete {weld_size}mm: DCR={dcr:.2f}'
        )

    def check_cjp_weld(self, force, weld_length, base_metal_thickness, base_Fu):
        """
        Verifica soldadura CJP (AISC J2.4).

        Returns:
            CheckResult
        """
        Fexx = self.props['Fexx']
        phi = 0.75

        # CJP: garganta = espesor del metal base
        a = base_metal_thickness

        # Resistencia del metal base controla generalmente
        Rn_weld = 0.60 * Fexx * a * weld_length / 1000  # kN
        Rn_base = 0.60 * base_Fu * a * weld_length / 1000  # kN

        Rn = min(Rn_weld, Rn_base)
        phi_Rn = phi * Rn

        dcr = force / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='CJP Weld',
            category='welds',
            passed=passed,
            demand=force,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J2.4',
            message=f'CJP: DCR={dcr:.2f}' if passed else f'FALLA: CJP: DCR={dcr:.2f}'
        )


class PlateValidator:
    """Validador de placas segun AISC J4."""

    def __init__(self, material='A36'):
        self.material = material
        self.props = AISCMaterialProperties.get_material(material)

    def check_gross_yielding(self, force, gross_area):
        """
        Verifica fluencia en area bruta (AISC J4.1).

        Args:
            force: Fuerza de tension (kN)
            gross_area: Area bruta (mm2)

        Returns:
            CheckResult
        """
        Fy = self.props['Fy']
        phi = 0.90

        Rn = Fy * gross_area / 1000  # kN
        phi_Rn = phi * Rn

        dcr = force / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Gross Yielding',
            category='plates',
            passed=passed,
            demand=force,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J4.1(a)',
            message=f'Fluencia bruta: DCR={dcr:.2f}'
        )

    def check_net_rupture(self, force, net_area):
        """
        Verifica ruptura en area neta (AISC J4.1).

        Returns:
            CheckResult
        """
        Fu = self.props['Fu']
        phi = 0.75

        Rn = Fu * net_area / 1000  # kN
        phi_Rn = phi * Rn

        dcr = force / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Net Rupture',
            category='plates',
            passed=passed,
            demand=force,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J4.1(b)',
            message=f'Ruptura neta: DCR={dcr:.2f}'
        )

    def check_block_shear(self, force, Agv, Anv, Ant, Ubs=1.0):
        """
        Verifica block shear (AISC J4.3).

        Args:
            force: Fuerza (kN)
            Agv: Area bruta en corte (mm2)
            Anv: Area neta en corte (mm2)
            Ant: Area neta en tension (mm2)
            Ubs: Factor de distribucion

        Returns:
            CheckResult
        """
        Fy = self.props['Fy']
        Fu = self.props['Fu']
        phi = 0.75

        # Dos ecuaciones, usar la menor
        Rn1 = (0.60 * Fu * Anv + Ubs * Fu * Ant) / 1000
        Rn2 = (0.60 * Fy * Agv + Ubs * Fu * Ant) / 1000

        Rn = min(Rn1, Rn2)
        phi_Rn = phi * Rn

        dcr = force / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Block Shear',
            category='plates',
            passed=passed,
            demand=force,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J4.3',
            message=f'Block shear: DCR={dcr:.2f}'
        )

    def check_shear_yielding(self, Vu, shear_area):
        """
        Verifica fluencia por corte (AISC J4.2).

        Returns:
            CheckResult
        """
        Fy = self.props['Fy']
        phi = 1.00

        Rn = 0.60 * Fy * shear_area / 1000  # kN
        phi_Rn = phi * Rn

        dcr = Vu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Shear Yielding',
            category='plates',
            passed=passed,
            demand=Vu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J4.2(a)',
            message=f'Fluencia corte: DCR={dcr:.2f}'
        )

    def check_shear_rupture(self, Vu, net_shear_area):
        """
        Verifica ruptura por corte (AISC J4.2).

        Returns:
            CheckResult
        """
        Fu = self.props['Fu']
        phi = 0.75

        Rn = 0.60 * Fu * net_shear_area / 1000  # kN
        phi_Rn = phi * Rn

        dcr = Vu / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Shear Rupture',
            category='plates',
            passed=passed,
            demand=Vu,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J4.2(b)',
            message=f'Ruptura corte: DCR={dcr:.2f}'
        )


class ColumnValidator:
    """Validador de efectos locales en columna segun AISC J10."""

    def __init__(self, column_profile, column_material='A992'):
        self.column = column_profile
        self.props = AISCMaterialProperties.get_material(column_material)

    def check_flange_local_bending(self, Pbf, beam_tf):
        """
        Verifica flexion local del patin (AISC J10.1).

        Args:
            Pbf: Fuerza del patin de viga (kN)
            beam_tf: Espesor del patin de viga (mm)

        Returns:
            CheckResult
        """
        Fyc = self.props['Fy']
        tfc = self.column.tf
        phi = 0.90

        Rn = 6.25 * tfc ** 2 * Fyc / 1000  # kN
        phi_Rn = phi * Rn

        dcr = Pbf / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Flange Local Bending',
            category='column',
            passed=passed,
            demand=Pbf,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J10.1',
            message=f'Flexion local patin: DCR={dcr:.2f}'
        )

    def check_web_local_yielding(self, Pbf, beam_tf, connection_type='interior'):
        """
        Verifica fluencia local del alma (AISC J10.2).

        Returns:
            CheckResult
        """
        Fyc = self.props['Fy']
        twc = self.column.tw
        k = self.column.k
        phi = 1.00

        if connection_type == 'interior':
            Rn = Fyc * twc * (5 * k + beam_tf) / 1000
        else:  # end
            Rn = Fyc * twc * (2.5 * k + beam_tf) / 1000

        phi_Rn = phi * Rn

        dcr = Pbf / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Web Local Yielding',
            category='column',
            passed=passed,
            demand=Pbf,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J10.2',
            message=f'Fluencia local alma: DCR={dcr:.2f}'
        )

    def check_web_local_crippling(self, Pbf, beam_tf, connection_type='interior'):
        """
        Verifica aplastamiento local del alma (AISC J10.3).

        Returns:
            CheckResult
        """
        twc = self.column.tw
        tfc = self.column.tf
        d = self.column.d
        Fyc = self.props['Fy']
        E = self.props['E']
        phi = 0.75

        lb = beam_tf  # Bearing length

        if connection_type == 'interior' or lb / d > 0.2:
            Rn = 0.80 * twc ** 2 * (1 + 3 * (lb / d) * (twc / tfc) ** 1.5) * math.sqrt(E * Fyc * tfc / twc) / 1000
        else:
            Rn = 0.40 * twc ** 2 * (1 + 3 * (lb / d) * (twc / tfc) ** 1.5) * math.sqrt(E * Fyc * tfc / twc) / 1000

        phi_Rn = phi * Rn

        dcr = Pbf / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Web Local Crippling',
            category='column',
            passed=passed,
            demand=Pbf,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J10.3',
            message=f'Aplastamiento alma: DCR={dcr:.2f}'
        )

    def check_panel_zone_shear(self, Vu_panel, db, beam_Fy=345):
        """
        Verifica corte en panel zone (AISC J10.6).

        Args:
            Vu_panel: Corte en panel zone (kN)
            db: Peralte de viga (mm)
            beam_Fy: Fy de viga (MPa)

        Returns:
            CheckResult
        """
        Fyc = self.props['Fy']
        twc = self.column.tw
        dc = self.column.d
        tfc = self.column.tf
        bfc = self.column.bf
        phi = 0.90

        # Sin efecto de doubler plate
        Rn = 0.60 * Fyc * dc * twc / 1000  # kN

        # Con contribucion de patines (para conexiones donde Pu <= 0.4Py)
        # Rn = 0.60 * Fyc * dc * twc * (1 + (3 * bfc * tfc**2) / (db * dc * twc))

        phi_Rn = phi * Rn

        dcr = Vu_panel / phi_Rn if phi_Rn > 0 else float('inf')
        passed = dcr <= 1.0

        return CheckResult(
            name='Panel Zone Shear',
            category='column',
            passed=passed,
            demand=Vu_panel,
            capacity=phi_Rn,
            dcr=dcr,
            reference='AISC J10.6',
            message=f'Panel zone: DCR={dcr:.2f}'
        )


class ConnectionValidator:
    """Validador principal de conexiones."""

    def __init__(self, code='AISC_360'):
        self.code = code

    def validate(self, connection_data, demand_shear=0, demand_moment=0,
                 beam_profile=None, column_profile=None):
        """
        Valida conexion completa.

        Args:
            connection_data: Datos de la conexion
            demand_shear: Demanda de corte (kN)
            demand_moment: Demanda de momento (kN-m)

        Returns:
            ValidationResult
        """
        checks = []
        warnings = []
        recommendations = []

        summary = connection_data.summary

        # Verificaciones de tornillos
        if summary['bolt_count'] > 0:
            bolt_validator = BoltValidator(
                summary['bolt_diameter'],
                summary['bolt_grade']
            )

            # Corte en tornillos
            check = bolt_validator.check_shear(
                demand_shear,
                summary['bolt_count']
            )
            checks.append(check)

            # Si hay momento, verificar tension
            if demand_moment > 0 and connection_data.type in ['end_plate', 'extended_end_plate']:
                # Estimar fuerza de tension en tornillos
                beam_d = 500  # Estimacion
                Tu = demand_moment * 1000 / (0.9 * beam_d)  # kN
                check = bolt_validator.check_tension(Tu, summary['bolt_count'] // 2)
                checks.append(check)

        # Verificaciones de capacidad general
        shear_cap = connection_data.shear_capacity
        moment_cap = connection_data.moment_capacity

        # DCR de corte
        dcr_shear = demand_shear / shear_cap if shear_cap > 0 else 0
        checks.append(CheckResult(
            name='Shear Capacity',
            category='connection',
            passed=dcr_shear <= 1.0,
            demand=demand_shear,
            capacity=shear_cap,
            dcr=dcr_shear,
            reference='General',
            message=f'Capacidad corte: DCR={dcr_shear:.2f}'
        ))

        # DCR de momento (si aplica)
        if moment_cap > 0 and demand_moment > 0:
            dcr_moment = demand_moment / moment_cap
            checks.append(CheckResult(
                name='Moment Capacity',
                category='connection',
                passed=dcr_moment <= 1.0,
                demand=demand_moment,
                capacity=moment_cap,
                dcr=dcr_moment,
                reference='General',
                message=f'Capacidad momento: DCR={dcr_moment:.2f}'
            ))

        # Verificaciones sismicas
        if summary['seismic_category'] != 'none':
            # Strong column - weak beam
            # Panel zone
            warnings.append(
                f"Conexion sismica {summary['seismic_category']}: "
                f"Verificar requisitos AISC 341 y AISC 358"
            )

        # Calcular DCR maximo
        dcr_max = max((c.dcr for c in checks if c.dcr != float('inf')), default=0)

        # Determinar si pasa
        is_valid = all(c.passed for c in checks)

        # Generar recomendaciones
        if dcr_max > 0.9:
            recommendations.append("DCR cercano al limite. Considerar aumentar capacidad.")

        if summary['bolt_count'] < 4:
            recommendations.append("Conexion con pocos tornillos. Verificar redundancia.")

        # Reporte
        report = {
            'code': self.code,
            'connection_type': connection_data.type,
            'is_valid': is_valid,
            'dcr_max': dcr_max,
            'checks_passed': sum(1 for c in checks if c.passed),
            'checks_total': len(checks),
            'demands': {
                'shear': demand_shear,
                'moment': demand_moment
            },
            'capacities': {
                'shear': shear_cap,
                'moment': moment_cap
            },
            'detailed_checks': [
                {
                    'name': c.name,
                    'passed': c.passed,
                    'demand': c.demand,
                    'capacity': c.capacity,
                    'dcr': c.dcr,
                    'reference': c.reference
                }
                for c in checks
            ]
        }

        return ValidationResult(
            is_valid=is_valid,
            checks=checks,
            dcr_max=dcr_max,
            warnings=warnings,
            report=report,
            recommendations=recommendations
        )


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    validator = ConnectionValidator(
        code=code if 'code' in dir() else 'AISC_360'
    )

    result = validator.validate(
        connection_data=connection_data if 'connection_data' in dir() else None,
        demand_shear=demand_shear if 'demand_shear' in dir() else 100,
        demand_moment=demand_moment if 'demand_moment' in dir() else 0
    )

    # Salidas para Grasshopper
    is_valid = result.is_valid
    checks = result.checks
    dcr_max = result.dcr_max
    warnings = result.warnings
    report = result.report
    recommendations = result.recommendations
