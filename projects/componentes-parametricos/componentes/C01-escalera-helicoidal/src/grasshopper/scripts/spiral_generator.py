"""
Spiral Generator - Escalera Helicoidal Parametrica
Genera la geometria base de la espiral y puntos de peldanos.

Inputs:
    floor_to_floor (float): Altura entre pisos (mm)
    outer_diameter (float): Diametro exterior (mm)
    inner_diameter (float): Diametro interior/columna (mm)
    rotation_angle (float): Angulo total de rotacion (grados)
    riser_height (float): Altura de contrahuella (mm)
    rotation_direction (str): "CCW" o "CW"
    start_angle (float): Angulo inicial (grados)

Outputs:
    spiral_curve (Curve): Curva espiral exterior
    inner_spiral (Curve): Curva espiral interior
    tread_planes (List[Plane]): Planos para cada peldano
    tread_count (int): Numero de peldanos
    geometry_data (dict): Datos geometricos
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de la espiral
SpiralData = namedtuple('SpiralData', [
    'outer_curve', 'inner_curve', 'center_line',
    'tread_planes', 'tread_points', 'tread_count',
    'actual_riser', 'actual_rotation', 'geometry_stats'
])

# Datos de peldano
TreadPosition = namedtuple('TreadPosition', [
    'index', 'plane', 'inner_point', 'outer_point',
    'angle', 'height', 'tread_depth_inner', 'tread_depth_outer'
])


class SpiralGeometry:
    """Generador de geometria espiral."""

    def __init__(self, tolerance=0.001):
        self.tolerance = tolerance

    def generate(self, floor_to_floor, outer_diameter, inner_diameter,
                 rotation_angle=360, riser_height=175,
                 rotation_direction='CCW', start_angle=0):
        """
        Genera la geometria completa de la espiral.

        Args:
            floor_to_floor: Altura entre pisos (mm)
            outer_diameter: Diametro exterior (mm)
            inner_diameter: Diametro interior (mm)
            rotation_angle: Rotacion total (grados)
            riser_height: Altura de peralte objetivo (mm)
            rotation_direction: 'CCW' (antihorario) o 'CW' (horario)
            start_angle: Angulo inicial (grados)

        Returns:
            SpiralData
        """
        # Validar y convertir parametros
        floor_to_floor = float(floor_to_floor)
        outer_radius = float(outer_diameter) / 2
        inner_radius = float(inner_diameter) / 2
        rotation_angle = float(rotation_angle)
        riser_height = float(riser_height)
        start_angle = float(start_angle)

        # Calcular numero de peldanos
        tread_count = int(math.ceil(floor_to_floor / riser_height))
        actual_riser = floor_to_floor / tread_count

        # Calcular rotacion por peldano
        rotation_per_tread = rotation_angle / tread_count
        actual_rotation = rotation_per_tread * tread_count

        # Factor de direccion
        direction_factor = 1 if rotation_direction == 'CCW' else -1

        # Generar puntos de peldanos
        tread_planes = []
        tread_points = []
        inner_points = []
        outer_points = []

        for i in range(tread_count + 1):  # +1 para incluir llegada
            # Angulo del peldano
            angle = start_angle + (direction_factor * rotation_per_tread * i)
            angle_rad = math.radians(angle)

            # Altura del peldano
            height = actual_riser * i

            # Punto interior
            inner_x = inner_radius * math.cos(angle_rad)
            inner_y = inner_radius * math.sin(angle_rad)
            inner_pt = rg.Point3d(inner_x, inner_y, height)
            inner_points.append(inner_pt)

            # Punto exterior
            outer_x = outer_radius * math.cos(angle_rad)
            outer_y = outer_radius * math.sin(angle_rad)
            outer_pt = rg.Point3d(outer_x, outer_y, height)
            outer_points.append(outer_pt)

            # Centro del peldano
            center_radius = (inner_radius + outer_radius) / 2
            center_x = center_radius * math.cos(angle_rad)
            center_y = center_radius * math.sin(angle_rad)
            center_pt = rg.Point3d(center_x, center_y, height)

            # Normal del plano (hacia arriba con inclinacion radial)
            radial_dir = rg.Vector3d(math.cos(angle_rad), math.sin(angle_rad), 0)
            tangent_dir = rg.Vector3d(-math.sin(angle_rad), math.cos(angle_rad), 0)
            if rotation_direction == 'CW':
                tangent_dir = -tangent_dir

            # Crear plano del peldano
            plane = rg.Plane(center_pt, tangent_dir, radial_dir)

            tread_planes.append(plane)

            # Calcular profundidades
            tread_depth_inner = self._calculate_tread_depth(
                inner_radius, rotation_per_tread
            )
            tread_depth_outer = self._calculate_tread_depth(
                outer_radius, rotation_per_tread
            )

            tread_pos = TreadPosition(
                index=i,
                plane=plane,
                inner_point=inner_pt,
                outer_point=outer_pt,
                angle=angle,
                height=height,
                tread_depth_inner=tread_depth_inner,
                tread_depth_outer=tread_depth_outer
            )
            tread_points.append(tread_pos)

        # Crear curvas espirales
        outer_curve = self._create_helix(
            outer_radius, floor_to_floor, rotation_angle,
            direction_factor, start_angle
        )
        inner_curve = self._create_helix(
            inner_radius, floor_to_floor, rotation_angle,
            direction_factor, start_angle
        )
        center_curve = self._create_helix(
            (inner_radius + outer_radius) / 2, floor_to_floor, rotation_angle,
            direction_factor, start_angle
        )

        # Estadisticas
        walkline_radius = inner_radius + 305  # 12" desde interior (IBC)
        walkline_tread = self._calculate_tread_depth(
            walkline_radius, rotation_per_tread
        )

        geometry_stats = {
            'floor_to_floor': floor_to_floor,
            'outer_diameter': outer_diameter,
            'inner_diameter': inner_diameter,
            'tread_count': tread_count,
            'actual_riser': actual_riser,
            'rotation_total': actual_rotation,
            'rotation_per_tread': rotation_per_tread,
            'tread_depth_inner': tread_depth_inner,
            'tread_depth_outer': tread_depth_outer,
            'walkline_radius': walkline_radius,
            'walkline_tread': walkline_tread,
            'stair_width': outer_radius - inner_radius,
            'helix_length': outer_curve.GetLength() if outer_curve else 0
        }

        return SpiralData(
            outer_curve=outer_curve,
            inner_curve=inner_curve,
            center_line=center_curve,
            tread_planes=tread_planes,
            tread_points=tread_points,
            tread_count=tread_count,
            actual_riser=actual_riser,
            actual_rotation=actual_rotation,
            geometry_stats=geometry_stats
        )

    def _create_helix(self, radius, height, rotation_angle,
                      direction_factor, start_angle):
        """
        Crea una curva helicoidal.

        Args:
            radius: Radio de la helice (mm)
            height: Altura total (mm)
            rotation_angle: Angulo de rotacion (grados)
            direction_factor: 1 para CCW, -1 para CW
            start_angle: Angulo inicial (grados)

        Returns:
            NurbsCurve
        """
        # Numero de puntos para la curva
        n_points = max(36, int(rotation_angle / 5))

        points = []
        for i in range(n_points + 1):
            t = i / n_points

            # Angulo en este punto
            angle = start_angle + (direction_factor * rotation_angle * t)
            angle_rad = math.radians(angle)

            # Altura en este punto
            z = height * t

            # Coordenadas
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)

            points.append(rg.Point3d(x, y, z))

        # Crear curva interpolada
        curve = rg.Curve.CreateInterpolatedCurve(
            points,
            3,  # Grado 3
            rg.CurveKnotStyle.ChordSquareRoot
        )

        return curve

    def _calculate_tread_depth(self, radius, rotation_per_tread):
        """
        Calcula la profundidad del peldano a un radio dado.

        La profundidad es el arco a ese radio.
        depth = 2 * pi * radius * (angle / 360)
        """
        angle_rad = math.radians(rotation_per_tread)
        depth = radius * angle_rad
        return depth


class SpiralOptimizer:
    """Optimiza parametros de la escalera."""

    def __init__(self, code='mexico_ntc'):
        """
        Args:
            code: Codigo de construccion a aplicar
        """
        self.code = code
        self._load_code_requirements()

    def _load_code_requirements(self):
        """Carga requisitos del codigo."""
        if self.code == 'mexico_ntc':
            self.riser_max = 200
            self.tread_min_walkline = 200
            self.walkline_offset = 305  # 12" desde interior
        elif self.code == 'ibc':
            self.riser_max = 190
            self.tread_min_walkline = 280
            self.walkline_offset = 305
        else:
            self.riser_max = 200
            self.tread_min_walkline = 250
            self.walkline_offset = 305

    def optimize_tread_count(self, floor_to_floor, outer_diameter, inner_diameter):
        """
        Encuentra el numero optimo de peldanos.

        Optimiza para cumplir:
        - Peralte <= maximo
        - Huella en linea de paso >= minimo

        Returns:
            dict: Configuracion optimizada
        """
        inner_radius = inner_diameter / 2
        walkline_radius = inner_radius + self.walkline_offset

        best_config = None
        best_score = float('inf')

        # Probar diferentes cantidades de peldanos
        min_treads = int(math.ceil(floor_to_floor / self.riser_max))
        max_treads = int(math.ceil(floor_to_floor / 140))  # Peralte minimo ~140

        for n_treads in range(min_treads, max_treads + 1):
            riser = floor_to_floor / n_treads

            # Probar diferentes angulos de rotacion
            for rotation in range(270, 721, 30):  # 270 a 720 grados
                rotation_per_tread = rotation / n_treads
                angle_rad = math.radians(rotation_per_tread)

                # Huella en linea de paso
                walkline_tread = walkline_radius * angle_rad

                # Verificar cumplimiento
                if riser > self.riser_max:
                    continue
                if walkline_tread < self.tread_min_walkline:
                    continue

                # Calcular score (menor es mejor)
                # Penalizar desviacion del peralte ideal (175mm)
                riser_score = abs(riser - 175) / 175

                # Penalizar huella muy grande (desperdicio) o muy pequena
                tread_score = abs(walkline_tread - 280) / 280

                # Penalizar rotacion excesiva
                rotation_score = (rotation - 270) / 450

                total_score = riser_score + tread_score + 0.5 * rotation_score

                if total_score < best_score:
                    best_score = total_score
                    best_config = {
                        'tread_count': n_treads,
                        'rotation_angle': rotation,
                        'riser_height': riser,
                        'rotation_per_tread': rotation_per_tread,
                        'walkline_tread': walkline_tread,
                        'score': total_score
                    }

        return best_config

    def validate_geometry(self, spiral_data):
        """
        Valida la geometria contra el codigo.

        Returns:
            dict: Resultados de validacion
        """
        stats = spiral_data.geometry_stats
        issues = []
        warnings = []

        # Verificar peralte
        if stats['actual_riser'] > self.riser_max:
            issues.append(
                f"Peralte {stats['actual_riser']:.0f}mm excede maximo {self.riser_max}mm"
            )
        elif stats['actual_riser'] > self.riser_max * 0.95:
            warnings.append(
                f"Peralte {stats['actual_riser']:.0f}mm cercano al limite"
            )

        # Verificar huella en linea de paso
        if stats['walkline_tread'] < self.tread_min_walkline:
            issues.append(
                f"Huella {stats['walkline_tread']:.0f}mm menor que minimo {self.tread_min_walkline}mm"
            )

        # Verificar ancho util
        if stats['stair_width'] < 600:
            issues.append(
                f"Ancho {stats['stair_width']:.0f}mm menor que minimo 600mm"
            )

        # Verificar proporcion 2R + H
        comfort_value = 2 * stats['actual_riser'] + stats['walkline_tread']
        if comfort_value < 550 or comfort_value > 700:
            warnings.append(
                f"Formula de confort: 2R+H = {comfort_value:.0f}mm (ideal: 600-660mm)"
            )

        is_valid = len(issues) == 0

        return {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'code': self.code,
            'checks': {
                'riser': stats['actual_riser'] <= self.riser_max,
                'tread': stats['walkline_tread'] >= self.tread_min_walkline,
                'width': stats['stair_width'] >= 600
            }
        }


class LandingGenerator:
    """Genera descansos intermedios y de llegada."""

    def __init__(self):
        self.tolerance = 0.001

    def create_landing(self, spiral_data, landing_angle, landing_width, landing_depth):
        """
        Crea un descanso en el angulo especificado.

        Args:
            spiral_data: Datos de la espiral
            landing_angle: Angulo donde insertar descanso (grados)
            landing_width: Ancho del descanso (mm)
            landing_depth: Profundidad del descanso (mm)

        Returns:
            dict: Datos del descanso
        """
        stats = spiral_data.geometry_stats

        # Encontrar altura en el angulo de descanso
        rotation_per_unit = stats['actual_rotation'] / stats['tread_count']
        treads_to_landing = landing_angle / rotation_per_unit
        landing_height = treads_to_landing * stats['actual_riser']

        # Crear geometria del descanso
        outer_radius = stats['outer_diameter'] / 2
        inner_radius = stats['inner_diameter'] / 2

        angle_rad = math.radians(landing_angle)

        # Puntos del descanso (sector circular)
        landing_arc = landing_depth / outer_radius
        start_angle = angle_rad - landing_arc / 2
        end_angle = angle_rad + landing_arc / 2

        points = []

        # Arco exterior
        for i in range(9):
            t = i / 8
            a = start_angle + t * (end_angle - start_angle)
            x = outer_radius * math.cos(a)
            y = outer_radius * math.sin(a)
            points.append(rg.Point3d(x, y, landing_height))

        # Arco interior (reverso)
        for i in range(9):
            t = 1 - i / 8
            a = start_angle + t * (end_angle - start_angle)
            x = inner_radius * math.cos(a)
            y = inner_radius * math.sin(a)
            points.append(rg.Point3d(x, y, landing_height))

        points.append(points[0])  # Cerrar

        # Crear superficie
        polyline = rg.Polyline(points)
        curve = polyline.ToNurbsCurve()

        return {
            'curve': curve,
            'height': landing_height,
            'angle': landing_angle,
            'width': landing_width,
            'depth': landing_depth,
            'treads_before': int(treads_to_landing)
        }


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    generator = SpiralGeometry()

    result = generator.generate(
        floor_to_floor=floor_to_floor if 'floor_to_floor' in dir() else 3000,
        outer_diameter=outer_diameter if 'outer_diameter' in dir() else 2000,
        inner_diameter=inner_diameter if 'inner_diameter' in dir() else 200,
        rotation_angle=rotation_angle if 'rotation_angle' in dir() else 360,
        riser_height=riser_height if 'riser_height' in dir() else 175,
        rotation_direction=rotation_direction if 'rotation_direction' in dir() else 'CCW',
        start_angle=start_angle if 'start_angle' in dir() else 0
    )

    # Validar
    optimizer = SpiralOptimizer(code='mexico_ntc')
    validation = optimizer.validate_geometry(result)

    # Salidas para Grasshopper
    spiral_curve = result.outer_curve
    inner_spiral = result.inner_curve
    tread_planes = result.tread_planes
    tread_count = result.tread_count
    geometry_data = result.geometry_stats
    is_valid = validation['is_valid']
    validation_issues = validation['issues']
