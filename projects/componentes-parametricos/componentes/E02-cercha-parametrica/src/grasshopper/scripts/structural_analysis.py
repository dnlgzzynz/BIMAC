"""
Structural Analysis - Cercha Parametrica
Analisis estructural simplificado y validacion.

Inputs:
    member_data (List[MemberData]): Datos de miembros
    node_data (List[NodeData]): Datos de nodos
    profile_results (List[SelectionResult]): Perfiles seleccionados
    loads (dict): Cargas aplicadas
    supports (dict): Condiciones de apoyo

Outputs:
    forces (List[float]): Fuerzas axiales (kN)
    reactions (dict): Reacciones en apoyos
    deflections (List[float]): Deflexiones (mm)
    validation_results (dict): Resultados de validacion
    is_valid (bool): Si la cercha cumple
"""

import math
from collections import namedtuple
from enum import Enum

# Tipos de carga
class LoadType(Enum):
    DEAD = "dead"
    LIVE = "live"
    SNOW = "snow"
    WIND = "wind"
    SEISMIC = "seismic"


# Resultados de analisis
AnalysisResult = namedtuple('AnalysisResult', [
    'forces', 'reactions', 'deflections',
    'max_tension', 'max_compression',
    'max_deflection', 'critical_member'
])

# Resultado de validacion
ValidationResult = namedtuple('ValidationResult', [
    'is_valid', 'checks', 'warnings', 'errors',
    'utilization_max', 'critical_member'
])


class SimpleTrussAnalysis:
    """
    Analisis simplificado de cercha por metodo de nodos.

    Nota: Este es un analisis simplificado para pre-dimensionamiento.
    Para diseno final, usar software de analisis estructural.
    """

    def __init__(self, E=200000):
        """
        Args:
            E: Modulo de elasticidad (MPa)
        """
        self.E = E  # MPa = N/mm2

    def analyze(self, member_data, node_data, loads, supports):
        """
        Ejecuta analisis de la cercha.

        Args:
            member_data: Lista de MemberData
            node_data: Lista de NodeData
            loads: Diccionario de cargas {tipo: valor_kN_m}
            supports: Diccionario de apoyos {nodo: tipo}

        Returns:
            AnalysisResult
        """
        # Calcular carga total
        total_load = self._calculate_total_load(loads)

        # Calcular fuerzas en miembros (metodo simplificado)
        forces = self._calculate_member_forces(member_data, node_data, total_load)

        # Calcular reacciones
        reactions = self._calculate_reactions(node_data, total_load, supports)

        # Calcular deflexiones (simplificado)
        deflections = self._calculate_deflections(member_data, forces)

        # Encontrar valores criticos
        max_tension = max(forces) if any(f > 0 for f in forces) else 0
        max_compression = min(forces) if any(f < 0 for f in forces) else 0
        max_deflection = max(abs(d) for d in deflections) if deflections else 0

        # Encontrar miembro critico
        max_force = max(abs(f) for f in forces)
        critical_idx = [i for i, f in enumerate(forces) if abs(f) == max_force][0]
        critical_member = member_data[critical_idx].id if critical_idx < len(member_data) else None

        return AnalysisResult(
            forces=forces,
            reactions=reactions,
            deflections=deflections,
            max_tension=max_tension,
            max_compression=max_compression,
            max_deflection=max_deflection,
            critical_member=critical_member
        )

    def _calculate_total_load(self, loads):
        """Calcula carga total factorizada."""
        # Factores de carga (LRFD)
        factors = {
            LoadType.DEAD: 1.2,
            LoadType.LIVE: 1.6,
            LoadType.SNOW: 1.6,
            LoadType.WIND: 1.0,
            LoadType.SEISMIC: 1.0,
        }

        total = 0
        for load_type, value in loads.items():
            if isinstance(load_type, str):
                load_type = LoadType[load_type.upper()]
            factor = factors.get(load_type, 1.0)
            total += factor * value

        return total

    def _calculate_member_forces(self, member_data, node_data, total_load):
        """
        Calcula fuerzas axiales en miembros.

        Metodo simplificado basado en analisis de celosia clasico.
        """
        forces = []

        # Obtener dimensiones de la cercha
        span = self._get_span(member_data)
        height = self._get_height(node_data)

        if span == 0 or height == 0:
            return [0] * len(member_data)

        # Carga distribuida en cuerda superior
        # Convertir a carga nodal
        n_bays = len([m for m in member_data if m.type.value == 'top_chord'])
        bay_width = span / n_bays if n_bays > 0 else span

        # Carga por nodo
        P_node = total_load * bay_width / 1000  # kN

        # Momento maximo en centro
        M_max = total_load * (span / 1000) ** 2 / 8  # kN-m

        for member in member_data:
            if member.type.value == 'top_chord':
                # Cuerda superior en compresion
                # F = M / h
                force = -M_max / (height / 1000) * 1.1  # Factor de seguridad
            elif member.type.value == 'bottom_chord':
                # Cuerda inferior en tension
                force = M_max / (height / 1000) * 1.1
            elif member.type.value == 'diagonal':
                # Diagonales en compresion o tension segun posicion
                angle_rad = math.radians(member.angle)
                shear = total_load * span / 2000  # Cortante maximo
                force = shear / math.sin(angle_rad) if math.sin(angle_rad) > 0.1 else 0
                # Alternar signo segun posicion
                if member.bay_index % 2 == 0:
                    force = -abs(force)
                else:
                    force = abs(force)
            else:  # vertical
                # Verticales generalmente en compresion
                force = -P_node * 0.5

            forces.append(force)

        return forces

    def _calculate_reactions(self, node_data, total_load, supports):
        """Calcula reacciones en apoyos."""
        # Encontrar nodos de apoyo
        support_nodes = [nd for nd in node_data if nd.is_support]

        if len(support_nodes) < 2:
            return {}

        # Para cercha simplemente apoyada
        # R_left = R_right = W*L/2 para carga uniforme
        span = self._get_span_from_nodes(node_data)
        total_W = total_load * span / 1000  # kN

        reactions = {}
        for i, node in enumerate(support_nodes):
            if i == 0:  # Apoyo izquierdo (fijo)
                reactions[node.id] = {
                    'Rx': 0,
                    'Ry': total_W / 2
                }
            else:  # Apoyo derecho (rodillo)
                reactions[node.id] = {
                    'Rx': 0,
                    'Ry': total_W / 2
                }

        return reactions

    def _calculate_deflections(self, member_data, forces):
        """
        Calcula deflexiones aproximadas.

        Usa metodo de trabajo virtual simplificado.
        """
        deflections = []

        for i, member in enumerate(member_data):
            # Deflexion axial = F * L / (A * E)
            force = forces[i] if i < len(forces) else 0
            length = member.length  # mm

            # Asumir area del perfil (cm2 -> mm2)
            A = 15 * 100  # 15 cm2 promedio

            delta = (force * 1000 * length) / (A * self.E) if A > 0 else 0
            deflections.append(delta)

        return deflections

    def _get_span(self, member_data):
        """Obtiene la luz de la cercha."""
        x_coords = []
        for m in member_data:
            x_coords.append(m.line.From.X)
            x_coords.append(m.line.To.X)

        if not x_coords:
            return 0

        return max(x_coords) - min(x_coords)

    def _get_span_from_nodes(self, node_data):
        """Obtiene la luz desde los nodos."""
        x_coords = [n.point.X for n in node_data]
        if not x_coords:
            return 0
        return max(x_coords) - min(x_coords)

    def _get_height(self, node_data):
        """Obtiene la altura de la cercha."""
        z_coords = [n.point.Z for n in node_data]
        if not z_coords:
            return 0
        return max(z_coords) - min(z_coords)


class TrussValidator:
    """Validador de cercha segun normas."""

    def __init__(self, code='AISC'):
        """
        Args:
            code: Codigo de diseno ('AISC', 'NTC')
        """
        self.code = code
        self.max_slenderness_chord = 200
        self.max_slenderness_web = 300
        self.deflection_limit = 240  # L/240

    def validate(self, member_data, profile_results, analysis_result, span):
        """
        Valida la cercha completa.

        Args:
            member_data: Datos de miembros
            profile_results: Perfiles seleccionados
            analysis_result: Resultado del analisis
            span: Luz de la cercha (mm)

        Returns:
            ValidationResult
        """
        checks = []
        warnings = []
        errors = []
        max_utilization = 0
        critical_member = None

        # 1. Verificar esbeltez de miembros
        slenderness_check = self._check_slenderness(member_data, profile_results)
        checks.append(slenderness_check)
        if not slenderness_check['pass']:
            errors.append(slenderness_check['message'])

        # 2. Verificar utilizacion de miembros
        utilization_check = self._check_utilization(
            member_data, profile_results, analysis_result.forces
        )
        checks.append(utilization_check)
        if not utilization_check['pass']:
            errors.append(utilization_check['message'])
        max_utilization = utilization_check.get('max_value', 0)
        critical_member = utilization_check.get('critical_member')

        # 3. Verificar deflexion
        deflection_check = self._check_deflection(
            analysis_result.max_deflection, span
        )
        checks.append(deflection_check)
        if not deflection_check['pass']:
            warnings.append(deflection_check['message'])

        # 4. Verificar angulos de diagonales
        angle_check = self._check_diagonal_angles(member_data)
        checks.append(angle_check)
        if not angle_check['pass']:
            warnings.append(angle_check['message'])

        # 5. Verificar ratio altura/luz
        ratio_check = self._check_height_ratio(member_data)
        checks.append(ratio_check)
        if not ratio_check['pass']:
            warnings.append(ratio_check['message'])

        # Determinar si es valida
        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            checks=checks,
            warnings=warnings,
            errors=errors,
            utilization_max=max_utilization,
            critical_member=critical_member
        )

    def _check_slenderness(self, member_data, profile_results):
        """Verifica esbeltez de miembros."""
        max_slenderness = 0
        failed_members = []

        for i, member in enumerate(member_data):
            # Encontrar perfil
            profile = None
            for pr in profile_results:
                if pr.member_id == member.id:
                    profile = pr.profile
                    slenderness = pr.slenderness
                    break

            if profile is None:
                continue

            # Limite segun tipo
            if member.type.value in ['top_chord', 'bottom_chord']:
                limit = self.max_slenderness_chord
            else:
                limit = self.max_slenderness_web

            if slenderness > limit:
                failed_members.append(member.id)

            max_slenderness = max(max_slenderness, slenderness)

        passed = len(failed_members) == 0

        return {
            'name': 'Esbeltez',
            'pass': passed,
            'max_value': max_slenderness,
            'limit': self.max_slenderness_chord,
            'failed_members': failed_members,
            'message': f"Esbeltez maxima: {max_slenderness:.0f}" if passed
                      else f"Esbeltez excedida en {len(failed_members)} miembros"
        }

    def _check_utilization(self, member_data, profile_results, forces):
        """Verifica utilizacion de miembros."""
        max_util = 0
        critical = None
        over_utilized = []

        for i, pr in enumerate(profile_results):
            util = pr.utilization
            if util > max_util:
                max_util = util
                critical = pr.member_id

            if util > 1.0:
                over_utilized.append(pr.member_id)

        passed = len(over_utilized) == 0

        return {
            'name': 'Utilizacion',
            'pass': passed,
            'max_value': max_util,
            'limit': 1.0,
            'critical_member': critical,
            'failed_members': over_utilized,
            'message': f"Utilizacion maxima: {max_util*100:.1f}%" if passed
                      else f"Capacidad excedida en {len(over_utilized)} miembros"
        }

    def _check_deflection(self, max_deflection, span):
        """Verifica deflexion maxima."""
        limit = span / self.deflection_limit
        ratio = max_deflection / limit if limit > 0 else 0

        passed = max_deflection <= limit

        return {
            'name': 'Deflexion',
            'pass': passed,
            'max_value': max_deflection,
            'limit': limit,
            'ratio': ratio,
            'message': f"Deflexion: {max_deflection:.1f}mm (L/{span/max_deflection:.0f})" if max_deflection > 0
                      else "Deflexion OK"
        }

    def _check_diagonal_angles(self, member_data):
        """Verifica angulos de diagonales."""
        angles = []
        out_of_range = []

        for member in member_data:
            if member.type.value == 'diagonal':
                angle = member.angle
                angles.append(angle)
                if angle < 30 or angle > 60:
                    out_of_range.append(member.id)

        if not angles:
            return {
                'name': 'Angulo diagonales',
                'pass': True,
                'message': "Sin diagonales"
            }

        avg_angle = sum(angles) / len(angles)
        passed = len(out_of_range) == 0

        return {
            'name': 'Angulo diagonales',
            'pass': passed,
            'avg_value': avg_angle,
            'range': (30, 60),
            'out_of_range': out_of_range,
            'message': f"Angulo promedio: {avg_angle:.1f}°" if passed
                      else f"{len(out_of_range)} diagonales fuera de rango 30-60°"
        }

    def _check_height_ratio(self, member_data):
        """Verifica ratio altura/luz."""
        # Calcular span y height
        x_coords = []
        z_coords = []

        for m in member_data:
            x_coords.extend([m.line.From.X, m.line.To.X])
            z_coords.extend([m.line.From.Z, m.line.To.Z])

        if not x_coords or not z_coords:
            return {'name': 'Ratio H/L', 'pass': True, 'message': "N/A"}

        span = max(x_coords) - min(x_coords)
        height = max(z_coords) - min(z_coords)

        ratio = height / span if span > 0 else 0

        passed = 0.05 <= ratio <= 0.25

        return {
            'name': 'Ratio H/L',
            'pass': passed,
            'value': ratio,
            'range': (0.05, 0.25),
            'message': f"Ratio H/L: {ratio:.3f}" if passed
                      else f"Ratio H/L: {ratio:.3f} (fuera de rango 0.05-0.25)"
        }


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    # Cargas por defecto (kN/m)
    default_loads = {
        'DEAD': 0.5,
        'LIVE': 1.0
    }

    # Apoyos por defecto
    default_supports = {
        'left': 'pinned',
        'right': 'roller'
    }

    analyzer = SimpleTrussAnalysis()
    analysis = analyzer.analyze(
        member_data=member_data if 'member_data' in dir() else [],
        node_data=node_data if 'node_data' in dir() else [],
        loads=loads if 'loads' in dir() else default_loads,
        supports=supports if 'supports' in dir() else default_supports
    )

    validator = TrussValidator()
    validation = validator.validate(
        member_data=member_data if 'member_data' in dir() else [],
        profile_results=profile_results if 'profile_results' in dir() else [],
        analysis_result=analysis,
        span=geometry_stats['span'] if 'geometry_stats' in dir() else 12000
    )

    # Salidas para Grasshopper
    forces = analysis.forces
    reactions = analysis.reactions
    deflections = analysis.deflections
    validation_results = {
        'checks': validation.checks,
        'warnings': validation.warnings,
        'errors': validation.errors,
        'max_utilization': validation.utilization_max
    }
    is_valid = validation.is_valid
