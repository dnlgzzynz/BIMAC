#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Estructura - C02 Rampa Vehicular Helicoidal

Genera elementos estructurales: vigas, columnas, muros
y cimentaciones para rampas helicoidales.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
BeamGeometry = namedtuple('BeamGeometry', [
    'brep', 'axis', 'profile', 'length', 'type', 'start_point', 'end_point'
])

ColumnGeometry = namedtuple('ColumnGeometry', [
    'brep', 'axis', 'profile', 'height', 'base_point', 'top_point', 'index'
])

WallGeometry = namedtuple('WallGeometry', [
    'brep', 'centerline', 'height', 'thickness', 'type'
])

FoundationGeometry = namedtuple('FoundationGeometry', [
    'brep', 'center', 'size', 'depth', 'type'
])


class BeamProfileDatabase:
    """Base de datos de perfiles de vigas."""

    PROFILES = {
        'W12x26': {'d': 310, 'bf': 165, 'tf': 10, 'tw': 6, 'weight': 38.7},
        'W14x30': {'d': 352, 'bf': 171, 'tf': 10, 'tw': 7, 'weight': 44.6},
        'W16x36': {'d': 403, 'bf': 178, 'tf': 11, 'tw': 8, 'weight': 53.6},
        'W18x40': {'d': 450, 'bf': 152, 'tf': 11, 'tw': 8, 'weight': 59.5},
        'W21x50': {'d': 529, 'bf': 166, 'tf': 13, 'tw': 9, 'weight': 74.4},
        'W24x68': {'d': 603, 'bf': 228, 'tf': 15, 'tw': 10, 'weight': 101.2},
    }

    @classmethod
    def get_profile(cls, name):
        return cls.PROFILES.get(name, cls.PROFILES['W14x30'])

    @classmethod
    def create_w_section(cls, name, plane):
        """Crea seccion W en el plano dado."""
        profile = cls.get_profile(name)

        d = profile['d'] / 1000.0
        bf = profile['bf'] / 1000.0
        tf = profile['tf'] / 1000.0
        tw = profile['tw'] / 1000.0

        # Crear contorno de seccion I
        points = [
            rg.Point3d(-bf/2, -d/2, 0),
            rg.Point3d(bf/2, -d/2, 0),
            rg.Point3d(bf/2, -d/2 + tf, 0),
            rg.Point3d(tw/2, -d/2 + tf, 0),
            rg.Point3d(tw/2, d/2 - tf, 0),
            rg.Point3d(bf/2, d/2 - tf, 0),
            rg.Point3d(bf/2, d/2, 0),
            rg.Point3d(-bf/2, d/2, 0),
            rg.Point3d(-bf/2, d/2 - tf, 0),
            rg.Point3d(-tw/2, d/2 - tf, 0),
            rg.Point3d(-tw/2, -d/2 + tf, 0),
            rg.Point3d(-bf/2, -d/2 + tf, 0),
        ]

        # Transformar al plano
        transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        transformed_points = []
        for pt in points:
            new_pt = rg.Point3d(pt)
            new_pt.Transform(transform)
            transformed_points.append(new_pt)

        # Crear polilinea cerrada
        polyline = rg.Polyline(transformed_points + [transformed_points[0]])
        return polyline.ToNurbsCurve()


class RadialBeamBuilder:
    """Construye vigas radiales de la rampa."""

    def __init__(self, helix_sections, profile_name='W14x30'):
        """
        Args:
            helix_sections: Lista de RampSection del generador
            profile_name: Perfil de viga
        """
        self.sections = helix_sections
        self.profile_name = profile_name
        self.profile = BeamProfileDatabase.get_profile(profile_name)

    def build_radial_beams(self, beam_spacing_angle=45):
        """
        Construye vigas radiales a intervalos angulares.

        Args:
            beam_spacing_angle: Espaciamiento angular en grados

        Returns:
            list: Lista de BeamGeometry
        """
        beams = []
        spacing_rad = math.radians(beam_spacing_angle)

        # Encontrar secciones en los angulos de vigas
        current_angle = 0
        section_dict = {s.angle: s for s in self.sections}
        angles = sorted(section_dict.keys())

        beam_angles = []
        while current_angle <= max(angles):
            beam_angles.append(current_angle)
            current_angle += spacing_rad

        for i, target_angle in enumerate(beam_angles):
            # Encontrar seccion mas cercana
            closest_angle = min(angles, key=lambda a: abs(a - target_angle))
            section = section_dict[closest_angle]

            # Crear viga radial
            beam = self._create_radial_beam(section, i)
            if beam:
                beams.append(beam)

        return beams

    def _create_radial_beam(self, section, index):
        """Crea una viga radial en la seccion dada."""
        start = section.inner_point
        end = section.outer_point

        # Offset hacia abajo por espesor de losa
        slab_thickness = 0.25
        start = rg.Point3d(start.X, start.Y, start.Z - slab_thickness)
        end = rg.Point3d(end.X, end.Y, end.Z - slab_thickness)

        # Eje de la viga
        axis = rg.Line(start, end)
        direction = rg.Vector3d(end - start)
        direction.Unitize()

        # Plano para el perfil
        up = rg.Vector3d(0, 0, 1)
        plane = rg.Plane(start, direction, up)

        # Crear perfil
        profile_curve = BeamProfileDatabase.create_w_section(
            self.profile_name, plane
        )

        if not profile_curve:
            return None

        # Extruir
        extrusion = rg.Extrusion.Create(profile_curve, axis.Length, True)

        return BeamGeometry(
            brep=extrusion.ToBrep() if extrusion else None,
            axis=axis,
            profile=self.profile_name,
            length=axis.Length,
            type='radial',
            start_point=start,
            end_point=end
        )


class PerimeterBeamBuilder:
    """Construye vigas perimetrales (interiores y exteriores)."""

    def __init__(self, helix_sections, inner_profile='W14x30',
                 outer_profile='W16x36'):
        """
        Args:
            helix_sections: Lista de RampSection
            inner_profile: Perfil viga interior
            outer_profile: Perfil viga exterior
        """
        self.sections = helix_sections
        self.inner_profile = inner_profile
        self.outer_profile = outer_profile

    def build_inner_beam(self, segment_count=20):
        """Construye viga perimetral interior."""
        return self._build_perimeter_beam(
            [s.inner_point for s in self.sections],
            self.inner_profile,
            'inner',
            segment_count
        )

    def build_outer_beam(self, segment_count=20):
        """Construye viga perimetral exterior."""
        return self._build_perimeter_beam(
            [s.outer_point for s in self.sections],
            self.outer_profile,
            'outer',
            segment_count
        )

    def _build_perimeter_beam(self, points, profile_name, beam_type,
                               segment_count):
        """Construye viga perimetral como sweep."""
        # Offset hacia abajo
        slab_thickness = 0.25
        offset_points = [
            rg.Point3d(p.X, p.Y, p.Z - slab_thickness)
            for p in points
        ]

        # Crear curva helicoidal
        curve = rg.NurbsCurve.Create(False, 3, offset_points)

        if not curve:
            return None

        # Crear perfil en el inicio
        start_plane = rg.Plane(curve.PointAtStart, curve.TangentAtStart)
        profile_curve = BeamProfileDatabase.create_w_section(
            profile_name, start_plane
        )

        if not profile_curve:
            return None

        # Sweep
        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(curve, profile_curve)

        return BeamGeometry(
            brep=breps[0] if breps else None,
            axis=curve,
            profile=profile_name,
            length=curve.GetLength(),
            type=beam_type,
            start_point=curve.PointAtStart,
            end_point=curve.PointAtEnd
        )


class ColumnBuilder:
    """Construye columnas de soporte."""

    def __init__(self, column_profile='D500', column_type='round'):
        """
        Args:
            column_profile: Perfil de columna (D500, 500x500, etc.)
            column_type: 'round' o 'square'
        """
        self.profile = column_profile
        self.column_type = column_type

        # Parsear dimension
        if column_type == 'round':
            self.diameter = float(column_profile[1:]) / 1000.0
        else:
            self.size = float(column_profile.split('x')[0]) / 1000.0

    def build_columns_at_sections(self, sections, angular_spacing=45,
                                   floor_elevation=0.0, position='inner'):
        """
        Construye columnas en ubicaciones especificas.

        Args:
            sections: Lista de RampSection
            angular_spacing: Espaciamiento angular (grados)
            floor_elevation: Elevacion del piso inferior
            position: 'inner', 'outer', o 'both'

        Returns:
            list: Lista de ColumnGeometry
        """
        columns = []
        spacing_rad = math.radians(angular_spacing)

        # Agrupar secciones por nivel angular
        section_by_angle = {}
        for s in sections:
            # Redondear angulo al espaciamiento
            rounded = round(s.angle / spacing_rad) * spacing_rad
            if rounded not in section_by_angle:
                section_by_angle[rounded] = []
            section_by_angle[rounded].append(s)

        col_index = 0
        for angle, angle_sections in sorted(section_by_angle.items()):
            if not angle_sections:
                continue

            # Tomar seccion representativa
            section = angle_sections[0]

            if position in ['inner', 'both']:
                col = self._create_column(
                    section.inner_point, floor_elevation, col_index
                )
                if col:
                    columns.append(col)
                    col_index += 1

            if position in ['outer', 'both']:
                col = self._create_column(
                    section.outer_point, floor_elevation, col_index
                )
                if col:
                    columns.append(col)
                    col_index += 1

        return columns

    def _create_column(self, top_point, floor_elevation, index):
        """Crea una columna individual."""
        # Puntos base y superior
        base = rg.Point3d(top_point.X, top_point.Y, floor_elevation)
        top = rg.Point3d(top_point.X, top_point.Y, top_point.Z - 0.25)

        height = top.Z - base.Z
        if height <= 0:
            return None

        # Crear perfil
        plane = rg.Plane(base, rg.Vector3d.ZAxis)

        if self.column_type == 'round':
            circle = rg.Circle(plane, self.diameter / 2)
            profile = circle.ToNurbsCurve()
        else:
            half = self.size / 2
            rect = rg.Rectangle3d(
                plane,
                rg.Interval(-half, half),
                rg.Interval(-half, half)
            )
            profile = rect.ToNurbsCurve()

        # Extruir
        extrusion = rg.Extrusion.Create(profile, height, True)

        return ColumnGeometry(
            brep=extrusion.ToBrep() if extrusion else None,
            axis=rg.Line(base, top),
            profile=self.profile,
            height=height,
            base_point=base,
            top_point=top,
            index=index
        )


class RetainingWallBuilder:
    """Construye muros de contencion."""

    def __init__(self, wall_thickness=0.30, wall_height=None):
        """
        Args:
            wall_thickness: Espesor del muro
            wall_height: Altura del muro (None = hasta piso)
        """
        self.thickness = wall_thickness
        self.height = wall_height

    def build_inner_wall(self, sections, floor_elevation=0.0):
        """Construye muro de contencion interior."""
        return self._build_helical_wall(
            [s.inner_point for s in sections],
            floor_elevation,
            'inner'
        )

    def build_outer_wall(self, sections, floor_elevation=0.0):
        """Construye muro de contencion exterior."""
        return self._build_helical_wall(
            [s.outer_point for s in sections],
            floor_elevation,
            'outer'
        )

    def _build_helical_wall(self, points, floor_elevation, wall_type):
        """Construye muro helicoidal."""
        # Puntos superiores
        top_points = points

        # Puntos inferiores
        if self.height:
            bottom_points = [
                rg.Point3d(p.X, p.Y, p.Z - self.height)
                for p in top_points
            ]
        else:
            bottom_points = [
                rg.Point3d(p.X, p.Y, floor_elevation)
                for p in top_points
            ]

        # Crear curvas
        top_curve = rg.NurbsCurve.Create(False, 3, top_points)
        bottom_curve = rg.NurbsCurve.Create(False, 3, bottom_points)

        if not top_curve or not bottom_curve:
            return None

        # Loft entre curvas
        loft = rg.Brep.CreateFromLoft(
            [bottom_curve, top_curve],
            rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal, False
        )

        if not loft:
            return None

        # Dar espesor
        surface = loft[0]

        # Offset para espesor
        if wall_type == 'inner':
            offset_dir = -1  # Hacia el centro
        else:
            offset_dir = 1   # Hacia afuera

        # Por simplicidad, crear como superficie
        avg_height = sum(t.Z - b.Z for t, b in
                         zip(top_points, bottom_points)) / len(top_points)

        return WallGeometry(
            brep=surface,
            centerline=top_curve,
            height=avg_height,
            thickness=self.thickness,
            type=wall_type
        )


class FoundationBuilder:
    """Construye cimentaciones."""

    def __init__(self, foundation_type='isolated'):
        """
        Args:
            foundation_type: 'isolated', 'combined', 'ring'
        """
        self.foundation_type = foundation_type

    def build_isolated_footings(self, columns, footing_size=1.5,
                                 footing_depth=0.6):
        """
        Construye zapatas aisladas bajo columnas.

        Args:
            columns: Lista de ColumnGeometry
            footing_size: Tamano de zapata (m)
            footing_depth: Profundidad de zapata (m)

        Returns:
            list: Lista de FoundationGeometry
        """
        footings = []

        for col in columns:
            center = col.base_point
            half = footing_size / 2

            # Crear caja de zapata
            plane = rg.Plane(
                rg.Point3d(center.X, center.Y, center.Z - footing_depth),
                rg.Vector3d.ZAxis
            )

            box = rg.Box(
                plane,
                rg.Interval(-half, half),
                rg.Interval(-half, half),
                rg.Interval(0, footing_depth)
            )

            footings.append(FoundationGeometry(
                brep=box.ToBrep(),
                center=center,
                size=footing_size,
                depth=footing_depth,
                type='isolated'
            ))

        return footings

    def build_ring_foundation(self, inner_radius, outer_radius,
                               ring_width=0.8, ring_depth=0.6,
                               floor_elevation=0.0):
        """
        Construye cimentacion de anillo.

        Args:
            inner_radius: Radio interior de la rampa
            outer_radius: Radio exterior de la rampa
            ring_width: Ancho del anillo
            ring_depth: Profundidad

        Returns:
            list: Lista de FoundationGeometry (interior y exterior)
        """
        foundations = []

        # Anillo interior
        inner_ring = self._create_ring(
            inner_radius - ring_width/2,
            inner_radius + ring_width/2,
            ring_depth,
            floor_elevation - ring_depth
        )

        if inner_ring:
            foundations.append(FoundationGeometry(
                brep=inner_ring,
                center=rg.Point3d(0, 0, floor_elevation - ring_depth),
                size=ring_width,
                depth=ring_depth,
                type='ring_inner'
            ))

        # Anillo exterior
        outer_ring = self._create_ring(
            outer_radius - ring_width/2,
            outer_radius + ring_width/2,
            ring_depth,
            floor_elevation - ring_depth
        )

        if outer_ring:
            foundations.append(FoundationGeometry(
                brep=outer_ring,
                center=rg.Point3d(0, 0, floor_elevation - ring_depth),
                size=ring_width,
                depth=ring_depth,
                type='ring_outer'
            ))

        return foundations

    def _create_ring(self, inner_r, outer_r, height, base_z):
        """Crea anillo de cimentacion."""
        # Circulos
        plane = rg.Plane(rg.Point3d(0, 0, base_z), rg.Vector3d.ZAxis)

        outer_circle = rg.Circle(plane, outer_r).ToNurbsCurve()
        inner_circle = rg.Circle(plane, inner_r).ToNurbsCurve()

        # Crear anillo
        outer_brep = rg.Extrusion.Create(outer_circle, height, True)
        inner_brep = rg.Extrusion.Create(inner_circle, height, True)

        if outer_brep and inner_brep:
            result = rg.Brep.CreateBooleanDifference(
                outer_brep.ToBrep(), inner_brep.ToBrep(), 0.001
            )
            if result and len(result) > 0:
                return result[0]

        return outer_brep.ToBrep() if outer_brep else None


class RampStructureAssembly:
    """Ensambla estructura completa de la rampa."""

    def __init__(self, helix_sections, inner_radius, outer_radius):
        """
        Args:
            helix_sections: Secciones de la rampa
            inner_radius: Radio interior
            outer_radius: Radio exterior
        """
        self.sections = helix_sections
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    def build_complete_structure(self, config=None):
        """
        Construye estructura completa.

        Args:
            config: Diccionario de configuracion

        Returns:
            dict: Diccionario con todos los elementos estructurales
        """
        if config is None:
            config = {
                'radial_beam_profile': 'W14x30',
                'radial_beam_spacing': 45,
                'inner_beam_profile': 'W14x30',
                'outer_beam_profile': 'W16x36',
                'column_profile': 'D500',
                'column_spacing': 45,
                'column_position': 'inner',
                'foundation_type': 'isolated',
                'floor_elevation': 0.0
            }

        result = {}

        # Vigas radiales
        radial_builder = RadialBeamBuilder(
            self.sections, config['radial_beam_profile']
        )
        result['radial_beams'] = radial_builder.build_radial_beams(
            config['radial_beam_spacing']
        )

        # Vigas perimetrales
        perim_builder = PerimeterBeamBuilder(
            self.sections,
            config['inner_beam_profile'],
            config['outer_beam_profile']
        )
        result['inner_beam'] = perim_builder.build_inner_beam()
        result['outer_beam'] = perim_builder.build_outer_beam()

        # Columnas
        col_builder = ColumnBuilder(config['column_profile'])
        result['columns'] = col_builder.build_columns_at_sections(
            self.sections,
            config['column_spacing'],
            config['floor_elevation'],
            config['column_position']
        )

        # Cimentaciones
        found_builder = FoundationBuilder(config['foundation_type'])

        if config['foundation_type'] == 'isolated':
            result['foundations'] = found_builder.build_isolated_footings(
                result['columns']
            )
        else:
            result['foundations'] = found_builder.build_ring_foundation(
                self.inner_radius,
                self.outer_radius,
                floor_elevation=config['floor_elevation']
            )

        return result


# Ejemplo de uso
if __name__ == "__main__":
    from helix_generator import HelicalRampGenerator, RampSurfaceBuilder
    from helix_generator import HelixCurveGenerator, SuperelevationCalculator

    # Generar secciones
    helix_gen = HelixCurveGenerator(7.5, 12.5, 3.0, 2.0)
    super_calc = SuperelevationCalculator(4.0)
    surface_builder = RampSurfaceBuilder(helix_gen, super_calc)
    sections = surface_builder.generate_sections()

    # Construir estructura
    assembly = RampStructureAssembly(sections, 7.5, 12.5)
    structure = assembly.build_complete_structure()

    print(f"Vigas radiales: {len(structure['radial_beams'])}")
    print(f"Columnas: {len(structure['columns'])}")
    print(f"Cimentaciones: {len(structure['foundations'])}")
