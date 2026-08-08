"""
Grid Generator - Muro Cortina Parametrico
Genera la grilla base para el sistema de muro cortina.

Inputs:
    surface (Surface): Superficie base del muro cortina
    u_count (int): Numero de divisiones en U
    v_count (int): Numero de divisiones en V
    module_width (float): Ancho objetivo del modulo (mm) - opcional
    module_height (float): Alto objetivo del modulo (mm) - opcional

Outputs:
    grid_curves_u (List[Curve]): Curvas de la grilla en direccion U
    grid_curves_v (List[Curve]): Curvas de la grilla en direccion V
    grid_points (DataTree[Point3d]): Puntos de interseccion
    panels (List[Surface]): Superficies de paneles
    cell_data (List[dict]): Datos de cada celda
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Tipos de datos
GridCell = namedtuple('GridCell', [
    'index_u', 'index_v', 'surface', 'corners',
    'center', 'normal', 'area', 'is_planar', 'curvature'
])

GridResult = namedtuple('GridResult', [
    'curves_u', 'curves_v', 'points', 'cells',
    'total_area', 'stats'
])


class CurtainWallGridGenerator:
    """Generador de grilla para muro cortina."""

    def __init__(self, tolerance=0.001):
        """
        Args:
            tolerance: Tolerancia geometrica (metros)
        """
        self.tolerance = tolerance
        self.min_cell_area = 0.1  # m2 minimo por celda

    def generate(self, surface, u_count, v_count,
                 module_width=None, module_height=None):
        """
        Genera la grilla sobre la superficie.

        Args:
            surface: Superficie base (Rhino.Geometry.Surface)
            u_count: Divisiones en U
            v_count: Divisiones en V
            module_width: Ancho objetivo (mm), ajusta u_count si se especifica
            module_height: Alto objetivo (mm), ajusta v_count si se especifica

        Returns:
            GridResult con todos los elementos generados
        """
        if surface is None:
            raise ValueError("Surface cannot be None")

        # Obtener dominios de la superficie
        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)

        # Ajustar divisiones si se especifican dimensiones objetivo
        if module_width is not None:
            u_count = self._calculate_divisions_by_size(
                surface, 0, module_width / 1000.0  # mm a m
            )
        if module_height is not None:
            v_count = self._calculate_divisions_by_size(
                surface, 1, module_height / 1000.0
            )

        # Asegurar valores minimos
        u_count = max(1, int(u_count))
        v_count = max(1, int(v_count))

        # Generar parametros de division
        u_params = self._divide_domain(u_domain, u_count)
        v_params = self._divide_domain(v_domain, v_count)

        # Generar curvas de grilla
        curves_u = self._generate_isocurves(surface, u_params, 0)
        curves_v = self._generate_isocurves(surface, v_params, 1)

        # Generar puntos de interseccion
        points = self._generate_grid_points(surface, u_params, v_params)

        # Generar celdas (paneles)
        cells = self._generate_cells(surface, u_params, v_params)

        # Calcular estadisticas
        stats = self._calculate_stats(cells)

        return GridResult(
            curves_u=curves_u,
            curves_v=curves_v,
            points=points,
            cells=cells,
            total_area=stats['total_area'],
            stats=stats
        )

    def _divide_domain(self, domain, count):
        """Divide un dominio en parametros equidistantes."""
        params = []
        for i in range(count + 1):
            t = i / float(count)
            param = domain.T0 + t * (domain.T1 - domain.T0)
            params.append(param)
        return params

    def _calculate_divisions_by_size(self, surface, direction, target_size):
        """
        Calcula el numero de divisiones para lograr un tamano objetivo.

        Args:
            surface: Superficie
            direction: 0 para U, 1 para V
            target_size: Tamano objetivo en metros

        Returns:
            int: Numero de divisiones recomendado
        """
        # Obtener curva isometrica en el medio
        domain = surface.Domain(direction)
        other_domain = surface.Domain(1 - direction)
        mid_param = (other_domain.T0 + other_domain.T1) / 2.0

        if direction == 0:
            iso_curve = surface.IsoCurve(1, mid_param)
        else:
            iso_curve = surface.IsoCurve(0, mid_param)

        if iso_curve is None:
            return 10  # Default

        length = iso_curve.GetLength()
        divisions = int(math.ceil(length / target_size))

        return max(1, divisions)

    def _generate_isocurves(self, surface, params, direction):
        """
        Genera curvas isometricas en la direccion especificada.

        Args:
            surface: Superficie
            params: Lista de parametros
            direction: 0 para curvas en U, 1 para curvas en V

        Returns:
            List[Curve]: Curvas isometricas
        """
        curves = []
        for param in params:
            iso = surface.IsoCurve(direction, param)
            if iso is not None:
                curves.append(iso)
        return curves

    def _generate_grid_points(self, surface, u_params, v_params):
        """
        Genera los puntos de interseccion de la grilla.

        Returns:
            List[List[Point3d]]: Matriz de puntos [u][v]
        """
        points = []
        for u in u_params:
            row = []
            for v in v_params:
                pt = surface.PointAt(u, v)
                row.append(pt)
            points.append(row)
        return points

    def _generate_cells(self, surface, u_params, v_params):
        """
        Genera las celdas (paneles) de la grilla.

        Returns:
            List[GridCell]: Lista de celdas con sus propiedades
        """
        cells = []

        for i in range(len(u_params) - 1):
            for j in range(len(v_params) - 1):
                # Parametros de la celda
                u0, u1 = u_params[i], u_params[i + 1]
                v0, v1 = v_params[j], v_params[j + 1]

                # Esquinas de la celda
                corners = [
                    surface.PointAt(u0, v0),
                    surface.PointAt(u1, v0),
                    surface.PointAt(u1, v1),
                    surface.PointAt(u0, v1)
                ]

                # Centro de la celda
                center = surface.PointAt((u0 + u1) / 2, (v0 + v1) / 2)

                # Normal en el centro
                normal = surface.NormalAt((u0 + u1) / 2, (v0 + v1) / 2)

                # Crear superficie de la celda
                cell_srf = self._create_cell_surface(surface, u0, u1, v0, v1)

                # Calcular area
                area = self._calculate_area(cell_srf)

                # Verificar planaridad
                is_planar, deviation = self._check_planarity(corners)

                # Calcular curvatura
                curvature = self._analyze_curvature(surface, (u0 + u1) / 2, (v0 + v1) / 2)

                cell = GridCell(
                    index_u=i,
                    index_v=j,
                    surface=cell_srf,
                    corners=corners,
                    center=center,
                    normal=normal,
                    area=area,
                    is_planar=is_planar,
                    curvature=curvature
                )
                cells.append(cell)

        return cells

    def _create_cell_surface(self, surface, u0, u1, v0, v1):
        """Crea una superficie trimmed para la celda."""
        # Crear intervalo de trim
        u_interval = rg.Interval(u0, u1)
        v_interval = rg.Interval(v0, v1)

        # Intentar crear superficie trimmed
        try:
            trimmed = surface.Trim(u_interval, v_interval)
            if trimmed is not None:
                return trimmed
        except:
            pass

        # Fallback: crear superficie desde esquinas
        corners = [
            surface.PointAt(u0, v0),
            surface.PointAt(u1, v0),
            surface.PointAt(u1, v1),
            surface.PointAt(u0, v1)
        ]

        return rg.NurbsSurface.CreateFromCorners(
            corners[0], corners[1], corners[2], corners[3]
        )

    def _calculate_area(self, surface):
        """Calcula el area de una superficie."""
        if surface is None:
            return 0.0

        props = rg.AreaMassProperties.Compute(surface)
        if props is not None:
            return props.Area
        return 0.0

    def _check_planarity(self, corners, tolerance=5.0):
        """
        Verifica si las esquinas son coplanares.

        Args:
            corners: Lista de 4 puntos
            tolerance: Tolerancia en mm

        Returns:
            tuple: (is_planar, max_deviation_mm)
        """
        if len(corners) != 4:
            return False, float('inf')

        # Crear plano desde 3 puntos
        plane_result, plane = rg.Plane.FitPlaneToPoints(corners)
        if plane_result != rg.PlaneFitResult.Success:
            return False, float('inf')

        # Medir desviacion maxima
        max_deviation = 0.0
        for pt in corners:
            dist = abs(plane.DistanceTo(pt))
            max_deviation = max(max_deviation, dist)

        # Convertir a mm
        max_deviation_mm = max_deviation * 1000

        return max_deviation_mm <= tolerance, max_deviation_mm

    def _analyze_curvature(self, surface, u, v):
        """
        Analiza la curvatura en un punto de la superficie.

        Returns:
            dict: Datos de curvatura
        """
        curvature = surface.CurvatureAt(u, v)
        if curvature is None:
            return {
                'gaussian': 0.0,
                'mean': 0.0,
                'k1': 0.0,
                'k2': 0.0,
                'type': 'flat'
            }

        gaussian = curvature.Gaussian
        mean = curvature.Mean
        k1 = curvature.Kappa(0)
        k2 = curvature.Kappa(1)

        # Clasificar tipo de curvatura
        if abs(gaussian) < 0.0001:
            if abs(mean) < 0.0001:
                curve_type = 'flat'
            else:
                curve_type = 'cylindrical'
        elif gaussian > 0:
            curve_type = 'synclastic'
        else:
            curve_type = 'anticlastic'

        return {
            'gaussian': gaussian,
            'mean': mean,
            'k1': k1,
            'k2': k2,
            'type': curve_type
        }

    def _calculate_stats(self, cells):
        """Calcula estadisticas de la grilla."""
        if not cells:
            return {
                'total_area': 0,
                'cell_count': 0,
                'planar_count': 0,
                'curved_count': 0,
                'planar_percent': 0,
                'min_area': 0,
                'max_area': 0,
                'avg_area': 0
            }

        areas = [c.area for c in cells]
        planar_count = sum(1 for c in cells if c.is_planar)

        return {
            'total_area': sum(areas),
            'cell_count': len(cells),
            'planar_count': planar_count,
            'curved_count': len(cells) - planar_count,
            'planar_percent': (planar_count / len(cells)) * 100 if cells else 0,
            'min_area': min(areas),
            'max_area': max(areas),
            'avg_area': sum(areas) / len(areas)
        }


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    # Variables de entrada de Grasshopper
    # surface, u_count, v_count, module_width, module_height

    generator = CurtainWallGridGenerator()

    result = generator.generate(
        surface=surface,
        u_count=u_count if 'u_count' in dir() else 10,
        v_count=v_count if 'v_count' in dir() else 5,
        module_width=module_width if 'module_width' in dir() else None,
        module_height=module_height if 'module_height' in dir() else None
    )

    # Salidas para Grasshopper
    grid_curves_u = result.curves_u
    grid_curves_v = result.curves_v
    grid_points = result.points
    panels = [cell.surface for cell in result.cells]
    cell_data = result.cells
    stats = result.stats
