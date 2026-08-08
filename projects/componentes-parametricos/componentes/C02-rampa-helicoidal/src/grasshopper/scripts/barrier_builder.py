#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Barreras - C02 Rampa Vehicular Helicoidal

Genera barreras vehiculares, barandales, drenaje y senalizacion
para rampas helicoidales.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
BarrierGeometry = namedtuple('BarrierGeometry', [
    'brep', 'centerline', 'type', 'height', 'length', 'test_level'
])

DrainageGeometry = namedtuple('DrainageGeometry', [
    'channel_brep', 'grates', 'piping', 'catch_basins'
])

MarkingGeometry = namedtuple('MarkingGeometry', [
    'curves', 'type', 'color', 'width'
])


class BarrierProfileDatabase:
    """Perfiles de barreras vehiculares."""

    PROFILES = {
        'f_shape': {
            'height': 0.810,
            'base_width': 0.610,
            'top_width': 0.150,
            'break_height': 0.330,
            'break_width': 0.230,
            'test_level': 'TL-4',
            'description': 'New Jersey modificado'
        },
        'jersey': {
            'height': 0.810,
            'base_width': 0.355,
            'top_width': 0.150,
            'break_height': 0.330,
            'break_width': 0.200,
            'test_level': 'TL-4',
            'description': 'Barrera Jersey estandar'
        },
        'single_slope': {
            'height': 0.810,
            'base_width': 0.230,
            'top_width': 0.150,
            'angle': 9.1,
            'test_level': 'TL-4',
            'description': 'Pendiente simple'
        },
        'low_profile': {
            'height': 0.510,
            'base_width': 0.355,
            'top_width': 0.150,
            'break_height': 0.200,
            'break_width': 0.180,
            'test_level': 'TL-2',
            'description': 'Perfil bajo interior'
        }
    }

    @classmethod
    def get_profile(cls, name):
        return cls.PROFILES.get(name, cls.PROFILES['jersey'])

    @classmethod
    def create_profile_curve(cls, name, plane):
        """
        Crea curva del perfil de barrera.

        Args:
            name: Nombre del perfil
            plane: Plano de ubicacion

        Returns:
            Curve: Perfil de la barrera
        """
        profile = cls.get_profile(name)

        h = profile['height']
        bw = profile['base_width']
        tw = profile['top_width']

        if name == 'single_slope':
            # Perfil de pendiente simple
            points = [
                rg.Point3d(0, 0, 0),
                rg.Point3d(bw, 0, 0),
                rg.Point3d(tw, 0, h),
                rg.Point3d(0, 0, h),
            ]
        else:
            # Perfil tipo Jersey/F-shape
            bh = profile.get('break_height', h * 0.4)
            bwm = profile.get('break_width', bw * 0.6)

            points = [
                rg.Point3d(0, 0, 0),
                rg.Point3d(bw, 0, 0),
                rg.Point3d(bwm, 0, bh),
                rg.Point3d(tw, 0, h),
                rg.Point3d(0, 0, h),
                rg.Point3d(0, 0, bh),
            ]

        # Cerrar perfil
        points.append(points[0])

        # Transformar al plano
        transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        transformed = []
        for pt in points:
            new_pt = rg.Point3d(pt)
            new_pt.Transform(transform)
            transformed.append(new_pt)

        polyline = rg.Polyline(transformed)
        return polyline.ToNurbsCurve()


class ConcreteBarrierBuilder:
    """Construye barreras de concreto."""

    def __init__(self, barrier_type='jersey'):
        """
        Args:
            barrier_type: Tipo de barrera
        """
        self.barrier_type = barrier_type
        self.profile_data = BarrierProfileDatabase.get_profile(barrier_type)

    def build_barrier_along_curve(self, path_curve, offset=0):
        """
        Construye barrera a lo largo de una curva.

        Args:
            path_curve: Curva de trayectoria
            offset: Offset lateral

        Returns:
            BarrierGeometry
        """
        if offset != 0:
            # Offset de la curva
            offset_curves = path_curve.Offset(
                rg.Plane.WorldXY, offset, 0.001, rg.CurveOffsetCornerStyle.Sharp
            )
            if offset_curves:
                path_curve = offset_curves[0]

        # Crear perfil en el inicio
        start_plane = rg.Plane(path_curve.PointAtStart, path_curve.TangentAtStart)

        # Rotar para que el perfil este vertical
        up = rg.Vector3d.ZAxis
        lateral = rg.Vector3d.CrossProduct(path_curve.TangentAtStart, up)
        start_plane = rg.Plane(path_curve.PointAtStart, lateral, up)

        profile = BarrierProfileDatabase.create_profile_curve(
            self.barrier_type, start_plane
        )

        if not profile:
            return None

        # Sweep
        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(path_curve, profile)

        if not breps:
            return None

        return BarrierGeometry(
            brep=breps[0],
            centerline=path_curve,
            type=self.barrier_type,
            height=self.profile_data['height'],
            length=path_curve.GetLength(),
            test_level=self.profile_data['test_level']
        )

    def build_inner_barrier(self, sections, offset=-0.1):
        """Construye barrera en borde interior."""
        points = [s.inner_point for s in sections]
        curve = rg.NurbsCurve.Create(False, 3, points)
        return self.build_barrier_along_curve(curve, offset)

    def build_outer_barrier(self, sections, offset=0.1):
        """Construye barrera en borde exterior."""
        points = [s.outer_point for s in sections]
        curve = rg.NurbsCurve.Create(False, 3, points)
        return self.build_barrier_along_curve(curve, offset)


class DrainageSystemBuilder:
    """Construye sistema de drenaje."""

    def __init__(self, channel_width=0.150, channel_depth=0.100):
        """
        Args:
            channel_width: Ancho del canal
            channel_depth: Profundidad del canal
        """
        self.channel_width = channel_width
        self.channel_depth = channel_depth

    def build_drainage_channel(self, sections, position='inner'):
        """
        Construye canal de drenaje perimetral.

        Args:
            sections: Secciones de la rampa
            position: 'inner' o 'outer'

        Returns:
            Brep: Canal de drenaje
        """
        if position == 'inner':
            points = [s.inner_point for s in sections]
        else:
            points = [s.outer_point for s in sections]

        # Crear curva base
        base_curve = rg.NurbsCurve.Create(False, 3, points)

        if not base_curve:
            return None

        # Crear perfil del canal (U invertida)
        start_plane = rg.Plane(
            base_curve.PointAtStart,
            base_curve.TangentAtStart
        )

        w = self.channel_width
        d = self.channel_depth

        profile_points = [
            rg.Point3d(-w/2, 0, 0),
            rg.Point3d(-w/2, 0, -d),
            rg.Point3d(w/2, 0, -d),
            rg.Point3d(w/2, 0, 0),
        ]

        # Transformar
        transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, start_plane)
        for pt in profile_points:
            pt.Transform(transform)

        polyline = rg.Polyline(profile_points)
        profile = polyline.ToNurbsCurve()

        # Sweep
        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(base_curve, profile)

        return breps[0] if breps else None

    def build_catch_basins(self, sections, spacing=15.0, position='inner'):
        """
        Construye registros de captacion.

        Args:
            sections: Secciones de la rampa
            spacing: Espaciamiento entre registros
            position: Ubicacion

        Returns:
            list: Lista de Brep
        """
        if position == 'inner':
            points = [s.inner_point for s in sections]
        else:
            points = [s.outer_point for s in sections]

        # Crear curva
        curve = rg.NurbsCurve.Create(False, 3, points)
        total_length = curve.GetLength()

        basins = []
        current_length = spacing / 2  # Empezar a media distancia

        while current_length < total_length:
            # Obtener punto y direccion
            t = current_length / total_length
            param = curve.Domain.ParameterAt(t)
            point = curve.PointAt(param)

            # Crear caja del registro
            basin_size = 0.450
            basin_depth = 0.600

            plane = rg.Plane(
                rg.Point3d(point.X, point.Y, point.Z - basin_depth),
                rg.Vector3d.ZAxis
            )

            box = rg.Box(
                plane,
                rg.Interval(-basin_size/2, basin_size/2),
                rg.Interval(-basin_size/2, basin_size/2),
                rg.Interval(0, basin_depth)
            )

            basins.append(box.ToBrep())
            current_length += spacing

        return basins

    def build_complete_drainage(self, sections):
        """Construye sistema de drenaje completo."""
        channel = self.build_drainage_channel(sections, 'inner')
        basins = self.build_catch_basins(sections, 15.0, 'inner')

        return DrainageGeometry(
            channel_brep=channel,
            grates=[],  # TODO: rejillas
            piping=[],  # TODO: tuberia
            catch_basins=basins
        )


class LaneMarkingBuilder:
    """Construye senalizacion horizontal."""

    def __init__(self, lane_width=3.25, marking_width=0.100):
        """
        Args:
            lane_width: Ancho de carril
            marking_width: Ancho de linea
        """
        self.lane_width = lane_width
        self.marking_width = marking_width

    def build_centerline(self, sections, lane_count=2):
        """
        Construye linea central.

        Args:
            sections: Secciones de la rampa
            lane_count: Numero de carriles

        Returns:
            MarkingGeometry
        """
        if lane_count < 2:
            return None

        # Crear linea en el centro de la rampa
        center_points = [s.center_point for s in sections]

        # Elevar ligeramente sobre la superficie
        elevated = [
            rg.Point3d(p.X, p.Y, p.Z + 0.005)
            for p in center_points
        ]

        curve = rg.NurbsCurve.Create(False, 3, elevated)

        return MarkingGeometry(
            curves=[curve],
            type='centerline',
            color='yellow',
            width=self.marking_width
        )

    def build_edge_lines(self, sections):
        """
        Construye lineas de borde.

        Returns:
            tuple: (inner_marking, outer_marking)
        """
        # Borde interior
        inner_points = [
            rg.Point3d(s.inner_point.X, s.inner_point.Y, s.inner_point.Z + 0.005)
            for s in sections
        ]
        inner_curve = rg.NurbsCurve.Create(False, 3, inner_points)

        inner_marking = MarkingGeometry(
            curves=[inner_curve],
            type='edge_line',
            color='white',
            width=self.marking_width
        )

        # Borde exterior
        outer_points = [
            rg.Point3d(s.outer_point.X, s.outer_point.Y, s.outer_point.Z + 0.005)
            for s in sections
        ]
        outer_curve = rg.NurbsCurve.Create(False, 3, outer_points)

        outer_marking = MarkingGeometry(
            curves=[outer_curve],
            type='edge_line',
            color='white',
            width=self.marking_width
        )

        return inner_marking, outer_marking

    def build_direction_arrows(self, sections, spacing=15.0):
        """
        Construye flechas de direccion.

        Args:
            sections: Secciones de la rampa
            spacing: Espaciamiento entre flechas

        Returns:
            list: Lista de curvas de flechas
        """
        center_points = [s.center_point for s in sections]
        curve = rg.NurbsCurve.Create(False, 3, center_points)
        total_length = curve.GetLength()

        arrows = []
        current = spacing

        while current < total_length - spacing:
            t = current / total_length
            param = curve.Domain.ParameterAt(t)

            point = curve.PointAt(param)
            tangent = curve.TangentAt(param)
            tangent.Unitize()

            # Crear flecha
            arrow = self._create_arrow(point, tangent, 2.0)
            if arrow:
                arrows.extend(arrow)

            current += spacing

        return arrows

    def _create_arrow(self, point, direction, length):
        """Crea geometria de flecha."""
        # Punto de inicio y fin
        start = rg.Point3d(
            point.X - direction.X * length/2,
            point.Y - direction.Y * length/2,
            point.Z + 0.005
        )
        end = rg.Point3d(
            point.X + direction.X * length/2,
            point.Y + direction.Y * length/2,
            point.Z + 0.005
        )

        # Linea principal
        main_line = rg.LineCurve(start, end)

        # Puntas de flecha
        lateral = rg.Vector3d.CrossProduct(direction, rg.Vector3d.ZAxis)
        lateral.Unitize()

        arrow_length = length * 0.3
        arrow_width = length * 0.2

        tip1 = rg.Point3d(
            end.X - direction.X * arrow_length + lateral.X * arrow_width,
            end.Y - direction.Y * arrow_length + lateral.Y * arrow_width,
            end.Z
        )
        tip2 = rg.Point3d(
            end.X - direction.X * arrow_length - lateral.X * arrow_width,
            end.Y - direction.Y * arrow_length - lateral.Y * arrow_width,
            end.Z
        )

        arrow1 = rg.LineCurve(end, tip1)
        arrow2 = rg.LineCurve(end, tip2)

        return [main_line, arrow1, arrow2]


class LightingBuilder:
    """Construye sistema de iluminacion."""

    def __init__(self, fixture_spacing=6.0, mounting_height=2.7):
        """
        Args:
            fixture_spacing: Espaciamiento entre luminarias
            mounting_height: Altura de montaje
        """
        self.spacing = fixture_spacing
        self.height = mounting_height

    def build_ceiling_lights(self, sections, inner_radius, outer_radius):
        """
        Construye luminarias de techo.

        Args:
            sections: Secciones de la rampa
            inner_radius: Radio interior
            outer_radius: Radio exterior

        Returns:
            list: Lista de puntos de luminarias
        """
        # Ubicar sobre linea central
        center_radius = (inner_radius + outer_radius) / 2

        lights = []
        total_angle = abs(sections[-1].angle - sections[0].angle)
        arc_length = center_radius * total_angle

        current = self.spacing / 2
        while current < arc_length:
            # Calcular angulo
            angle = (current / arc_length) * total_angle + sections[0].angle

            # Encontrar elevacion
            t = current / arc_length
            elevation = sections[0].elevation + t * (
                sections[-1].elevation - sections[0].elevation
            )

            # Punto de luminaria
            x = center_radius * math.cos(angle)
            y = center_radius * math.sin(angle)
            z = elevation + self.height

            lights.append(rg.Point3d(x, y, z))
            current += self.spacing

        return lights

    def build_light_fixture(self, location):
        """
        Crea geometria de luminaria.

        Args:
            location: Punto de ubicacion

        Returns:
            Brep: Geometria de luminaria
        """
        # Luminaria tipo panel rectangular
        width = 0.600
        length = 1.200
        depth = 0.050

        plane = rg.Plane(location, rg.Vector3d.ZAxis)

        box = rg.Box(
            plane,
            rg.Interval(-width/2, width/2),
            rg.Interval(-length/2, length/2),
            rg.Interval(-depth, 0)
        )

        return box.ToBrep()


class RampAccessoriesAssembly:
    """Ensambla accesorios completos de la rampa."""

    def __init__(self, sections, inner_radius, outer_radius):
        """
        Args:
            sections: Secciones de la rampa
            inner_radius: Radio interior
            outer_radius: Radio exterior
        """
        self.sections = sections
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    def build_all_accessories(self, config=None):
        """
        Construye todos los accesorios.

        Args:
            config: Diccionario de configuracion

        Returns:
            dict: Diccionario con accesorios
        """
        if config is None:
            config = {
                'barrier_type': 'jersey',
                'lane_count': 2,
                'drainage': True,
                'lighting': True
            }

        result = {}

        # Barreras
        barrier_builder = ConcreteBarrierBuilder(config['barrier_type'])
        result['inner_barrier'] = barrier_builder.build_inner_barrier(
            self.sections
        )
        result['outer_barrier'] = barrier_builder.build_outer_barrier(
            self.sections
        )

        # Drenaje
        if config.get('drainage', True):
            drainage_builder = DrainageSystemBuilder()
            result['drainage'] = drainage_builder.build_complete_drainage(
                self.sections
            )

        # Senalizacion
        marking_builder = LaneMarkingBuilder()
        result['centerline'] = marking_builder.build_centerline(
            self.sections, config['lane_count']
        )
        result['edge_lines'] = marking_builder.build_edge_lines(self.sections)
        result['arrows'] = marking_builder.build_direction_arrows(self.sections)

        # Iluminacion
        if config.get('lighting', True):
            light_builder = LightingBuilder()
            result['light_points'] = light_builder.build_ceiling_lights(
                self.sections, self.inner_radius, self.outer_radius
            )

        return result


# Ejemplo de uso
if __name__ == "__main__":
    from helix_generator import HelixCurveGenerator, SuperelevationCalculator
    from helix_generator import RampSurfaceBuilder

    # Generar secciones
    helix_gen = HelixCurveGenerator(7.5, 12.5, 3.0, 2.0)
    super_calc = SuperelevationCalculator(4.0)
    surface_builder = RampSurfaceBuilder(helix_gen, super_calc)
    sections = surface_builder.generate_sections()

    # Construir accesorios
    assembly = RampAccessoriesAssembly(sections, 7.5, 12.5)
    accessories = assembly.build_all_accessories()

    print(f"Barreras construidas: interior y exterior")
    print(f"Registros de drenaje: {len(accessories['drainage'].catch_basins)}")
    print(f"Luminarias: {len(accessories['light_points'])}")
