"""
Mullion Builder - Muro Cortina Parametrico
Genera los perfiles de mullions y travesanos.

Inputs:
    grid_curves_u (List[Curve]): Curvas verticales (mullions)
    grid_curves_v (List[Curve]): Curvas horizontales (transoms)
    mullion_width (float): Ancho del mullion (mm)
    mullion_depth (float): Profundidad del mullion (mm)
    transom_width (float): Ancho del travesano (mm)
    transom_depth (float): Profundidad del travesano (mm)
    profile_type (str): Tipo de perfil (standard/thermal/structural)

Outputs:
    mullions (List[Brep]): Geometria de mullions
    transoms (List[Brep]): Geometria de travesanos
    connections (List[Brep]): Piezas de conexion
    profiles_data (List[dict]): Datos de cada perfil
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Tipos de perfil
ProfileData = namedtuple('ProfileData', [
    'type', 'curve', 'brep', 'length', 'section_area',
    'weight', 'thermal_break', 'start_point', 'end_point'
])

MullionResult = namedtuple('MullionResult', [
    'mullions', 'transoms', 'connections',
    'total_length_mullions', 'total_length_transoms',
    'total_weight', 'profiles_data'
])


class MullionProfile:
    """Define el perfil de seccion del mullion."""

    # Densidad del aluminio (kg/m3)
    ALUMINUM_DENSITY = 2700

    def __init__(self, width, depth, wall_thickness=3.0,
                 profile_type='standard', thermal_break=False):
        """
        Args:
            width: Ancho del perfil (mm)
            depth: Profundidad del perfil (mm)
            wall_thickness: Espesor de pared (mm)
            profile_type: standard | thermal | structural
            thermal_break: Si tiene rotura de puente termico
        """
        self.width = width / 1000.0  # Convertir a metros
        self.depth = depth / 1000.0
        self.wall_thickness = wall_thickness / 1000.0
        self.profile_type = profile_type
        self.thermal_break = thermal_break or (profile_type == 'thermal')

        # Calcular propiedades
        self.section_area = self._calculate_section_area()
        self.weight_per_meter = self.section_area * self.ALUMINUM_DENSITY

    def _calculate_section_area(self):
        """Calcula el area de la seccion transversal."""
        if self.profile_type == 'structural':
            # Perfil solido con cavidades
            outer_area = self.width * self.depth
            inner_width = self.width - 2 * self.wall_thickness
            inner_depth = self.depth - 2 * self.wall_thickness
            inner_area = inner_width * inner_depth * 0.7  # 70% hueco
            return outer_area - inner_area

        elif self.profile_type == 'thermal':
            # Perfil con rotura de puente termico (2 camaras)
            outer_area = self.width * self.depth
            chamber_area = (self.width - 2 * self.wall_thickness) * \
                           (self.depth - 2 * self.wall_thickness) * 0.6
            return outer_area - chamber_area

        else:  # standard
            # Perfil tubular simple
            outer_area = self.width * self.depth
            inner_area = (self.width - 2 * self.wall_thickness) * \
                         (self.depth - 2 * self.wall_thickness)
            return outer_area - inner_area

    def create_section_curve(self):
        """
        Crea la curva de seccion del perfil.

        Returns:
            Curve: Curva cerrada del perfil
        """
        w = self.width / 2
        d = self.depth / 2
        t = self.wall_thickness

        if self.profile_type == 'structural':
            # Perfil I estructural
            points = [
                rg.Point3d(-w, -d, 0),
                rg.Point3d(w, -d, 0),
                rg.Point3d(w, -d + t, 0),
                rg.Point3d(t/2, -d + t, 0),
                rg.Point3d(t/2, d - t, 0),
                rg.Point3d(w, d - t, 0),
                rg.Point3d(w, d, 0),
                rg.Point3d(-w, d, 0),
                rg.Point3d(-w, d - t, 0),
                rg.Point3d(-t/2, d - t, 0),
                rg.Point3d(-t/2, -d + t, 0),
                rg.Point3d(-w, -d + t, 0),
                rg.Point3d(-w, -d, 0)
            ]
        else:
            # Perfil rectangular hueco
            # Exterior
            outer = [
                rg.Point3d(-w, -d, 0),
                rg.Point3d(w, -d, 0),
                rg.Point3d(w, d, 0),
                rg.Point3d(-w, d, 0),
                rg.Point3d(-w, -d, 0)
            ]
            points = outer

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()


class MullionBuilder:
    """Construye los mullions y travesanos del muro cortina."""

    def __init__(self):
        self.tolerance = 0.001

    def build(self, grid_curves_u, grid_curves_v,
              mullion_width=65, mullion_depth=150,
              transom_width=50, transom_depth=120,
              profile_type='standard'):
        """
        Construye todos los perfiles del muro cortina.

        Args:
            grid_curves_u: Curvas verticales
            grid_curves_v: Curvas horizontales
            mullion_width: Ancho mullion (mm)
            mullion_depth: Profundidad mullion (mm)
            transom_width: Ancho travesano (mm)
            transom_depth: Profundidad travesano (mm)
            profile_type: Tipo de perfil

        Returns:
            MullionResult
        """
        # Crear perfiles
        mullion_profile = MullionProfile(
            mullion_width, mullion_depth,
            profile_type=profile_type
        )
        transom_profile = MullionProfile(
            transom_width, transom_depth,
            profile_type=profile_type
        )

        # Generar mullions (verticales)
        mullions = []
        mullion_data = []
        total_length_mullions = 0

        for curve in grid_curves_u:
            if curve is None:
                continue

            brep = self._sweep_profile(curve, mullion_profile)
            length = curve.GetLength()
            total_length_mullions += length

            data = ProfileData(
                type='mullion',
                curve=curve,
                brep=brep,
                length=length,
                section_area=mullion_profile.section_area,
                weight=length * mullion_profile.weight_per_meter,
                thermal_break=mullion_profile.thermal_break,
                start_point=curve.PointAtStart,
                end_point=curve.PointAtEnd
            )
            mullions.append(brep)
            mullion_data.append(data)

        # Generar travesanos (horizontales)
        transoms = []
        transom_data = []
        total_length_transoms = 0

        for curve in grid_curves_v:
            if curve is None:
                continue

            brep = self._sweep_profile(curve, transom_profile)
            length = curve.GetLength()
            total_length_transoms += length

            data = ProfileData(
                type='transom',
                curve=curve,
                brep=brep,
                length=length,
                section_area=transom_profile.section_area,
                weight=length * transom_profile.weight_per_meter,
                thermal_break=transom_profile.thermal_break,
                start_point=curve.PointAtStart,
                end_point=curve.PointAtEnd
            )
            transoms.append(brep)
            transom_data.append(data)

        # Generar conexiones en intersecciones
        connections = self._generate_connections(
            grid_curves_u, grid_curves_v,
            mullion_profile, transom_profile
        )

        # Calcular peso total
        total_weight = sum(d.weight for d in mullion_data)
        total_weight += sum(d.weight for d in transom_data)
        # Agregar 10% por conexiones
        total_weight *= 1.10

        all_profiles = mullion_data + transom_data

        return MullionResult(
            mullions=mullions,
            transoms=transoms,
            connections=connections,
            total_length_mullions=total_length_mullions,
            total_length_transoms=total_length_transoms,
            total_weight=total_weight,
            profiles_data=all_profiles
        )

    def _sweep_profile(self, curve, profile):
        """
        Crea un barrido del perfil a lo largo de la curva.

        Args:
            curve: Curva guia
            profile: MullionProfile

        Returns:
            Brep: Geometria del perfil
        """
        if curve is None:
            return None

        # Obtener frame al inicio de la curva
        success, plane = curve.PerpendicularFrameAt(curve.Domain.T0)
        if not success:
            plane = rg.Plane.WorldXY
            plane.Origin = curve.PointAtStart

        # Crear seccion del perfil
        section = profile.create_section_curve()

        # Transformar seccion al plano
        xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        section.Transform(xform)

        # Crear barrido
        sweep = rg.Brep.CreateFromSweep(
            curve,
            section,
            closed=False,
            tolerance=self.tolerance
        )

        if sweep and len(sweep) > 0:
            return sweep[0]

        # Fallback: extrusion simple
        return self._create_extrusion_fallback(curve, profile)

    def _create_extrusion_fallback(self, curve, profile):
        """Crea una extrusion como alternativa al sweep."""
        # Obtener puntos inicial y final
        start_pt = curve.PointAtStart
        end_pt = curve.PointAtEnd

        # Crear caja orientada
        direction = end_pt - start_pt
        length = direction.Length

        if length < self.tolerance:
            return None

        direction.Unitize()

        # Crear plano base
        plane = rg.Plane(start_pt, direction)

        # Crear rectangulo del perfil
        w = profile.width / 2
        d = profile.depth / 2
        rect = rg.Rectangle3d(plane, rg.Interval(-w, w), rg.Interval(-d, d))

        # Extruir
        extrusion = rg.Extrusion.Create(
            rect.ToNurbsCurve(),
            length,
            True  # cap
        )

        if extrusion:
            return extrusion.ToBrep()
        return None

    def _generate_connections(self, curves_u, curves_v,
                               mullion_profile, transom_profile):
        """
        Genera piezas de conexion en las intersecciones.

        Returns:
            List[Brep]: Conexiones
        """
        connections = []

        # Encontrar intersecciones
        for u_curve in curves_u:
            if u_curve is None:
                continue

            for v_curve in curves_v:
                if v_curve is None:
                    continue

                # Buscar interseccion
                intersections = rg.Intersect.Intersection.CurveCurve(
                    u_curve, v_curve, self.tolerance, self.tolerance
                )

                if intersections is None:
                    continue

                for event in intersections:
                    if event.IsPoint:
                        pt = event.PointA

                        # Crear pieza de conexion (cubo)
                        connection = self._create_connection_piece(
                            pt, mullion_profile, transom_profile
                        )
                        if connection:
                            connections.append(connection)

        return connections

    def _create_connection_piece(self, point, mullion_profile, transom_profile):
        """
        Crea una pieza de conexion en un punto.

        Args:
            point: Punto de interseccion
            mullion_profile: Perfil del mullion
            transom_profile: Perfil del travesano

        Returns:
            Brep: Pieza de conexion
        """
        # Dimensiones de la conexion
        w = max(mullion_profile.width, transom_profile.width) * 1.1
        d = max(mullion_profile.depth, transom_profile.depth) * 1.1
        h = transom_profile.width * 1.5  # Altura

        # Crear caja centrada en el punto
        plane = rg.Plane(point, rg.Vector3d.ZAxis)
        box = rg.Box(
            plane,
            rg.Interval(-w/2, w/2),
            rg.Interval(-d/2, d/2),
            rg.Interval(-h/2, h/2)
        )

        return box.ToBrep()


class MullionOptimizer:
    """Optimiza la configuracion de mullions."""

    def __init__(self, wind_load=1.2, max_deflection_ratio=175):
        """
        Args:
            wind_load: Carga de viento (kPa)
            max_deflection_ratio: Ratio L/n para deflexion maxima
        """
        self.wind_load = wind_load
        self.max_deflection_ratio = max_deflection_ratio
        self.E_aluminum = 69000  # MPa (modulo de elasticidad)

    def calculate_required_depth(self, span, width, tributary_width):
        """
        Calcula la profundidad requerida del mullion.

        Args:
            span: Luz del mullion (mm)
            width: Ancho del mullion (mm)
            tributary_width: Ancho tributario (mm)

        Returns:
            float: Profundidad requerida (mm)
        """
        # Convertir a metros
        span_m = span / 1000.0
        width_m = width / 1000.0
        trib_m = tributary_width / 1000.0

        # Carga lineal (kN/m)
        w = self.wind_load * trib_m

        # Deflexion maxima permitida
        delta_max = span_m / self.max_deflection_ratio

        # Momento de inercia requerido (m4)
        # delta = 5*w*L^4 / (384*E*I)
        # I = 5*w*L^4 / (384*E*delta)
        I_req = (5 * w * span_m**4) / (384 * self.E_aluminum * 1e6 * delta_max)

        # Para seccion rectangular: I = b*h^3/12
        # h = (12*I/b)^(1/3)
        depth_m = (12 * I_req / width_m) ** (1.0/3.0)

        # Convertir a mm y agregar factor de seguridad
        depth_mm = depth_m * 1000 * 1.2

        # Redondear a multiplos de 5mm
        depth_mm = math.ceil(depth_mm / 5) * 5

        return max(depth_mm, 100)  # Minimo 100mm

    def recommend_profile(self, span, tributary_width, glass_weight=25):
        """
        Recomienda el tipo de perfil optimo.

        Args:
            span: Luz (mm)
            tributary_width: Ancho tributario (mm)
            glass_weight: Peso del vidrio (kg/m2)

        Returns:
            dict: Recomendacion de perfil
        """
        # Calcular profundidad requerida
        req_depth = self.calculate_required_depth(span, 65, tributary_width)

        if req_depth <= 120:
            profile_type = 'standard'
            width = 50
            depth = 120
        elif req_depth <= 180:
            profile_type = 'standard'
            width = 65
            depth = 150
        elif req_depth <= 220:
            profile_type = 'thermal'
            width = 65
            depth = 200
        else:
            profile_type = 'structural'
            width = 80
            depth = min(250, int(req_depth))

        return {
            'profile_type': profile_type,
            'width': width,
            'depth': depth,
            'required_depth': req_depth,
            'span': span,
            'deflection_ratio': self.max_deflection_ratio
        }


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    # Variables de entrada de Grasshopper
    # grid_curves_u, grid_curves_v, mullion_width, mullion_depth,
    # transom_width, transom_depth, profile_type

    builder = MullionBuilder()

    result = builder.build(
        grid_curves_u=grid_curves_u,
        grid_curves_v=grid_curves_v,
        mullion_width=mullion_width if 'mullion_width' in dir() else 65,
        mullion_depth=mullion_depth if 'mullion_depth' in dir() else 150,
        transom_width=transom_width if 'transom_width' in dir() else 50,
        transom_depth=transom_depth if 'transom_depth' in dir() else 120,
        profile_type=profile_type if 'profile_type' in dir() else 'standard'
    )

    # Salidas para Grasshopper
    mullions = result.mullions
    transoms = result.transoms
    connections = result.connections
    profiles_data = result.profiles_data
    total_weight = result.total_weight
