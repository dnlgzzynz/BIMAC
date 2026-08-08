"""
Tread Builder - Escalera Helicoidal Parametrica
Genera los peldanos y estructura de soporte.

Inputs:
    spiral_data (SpiralData): Datos de la espiral
    tread_thickness (float): Espesor del peldano (mm)
    nosing (float): Proyeccion de nariz (mm)
    tread_material (str): Material del peldano
    open_riser (bool): Contrahuella abierta
    structure_type (str): Tipo de estructura

Outputs:
    treads (List[Brep]): Geometria de peldanos
    risers (List[Brep]): Geometria de contrahuellas
    structure (List[Brep]): Estructura de soporte
    tread_data (List[dict]): Datos de cada peldano
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos del peldano construido
TreadGeometry = namedtuple('TreadGeometry', [
    'index', 'brep', 'area', 'inner_edge', 'outer_edge',
    'nosing_edge', 'material', 'weight'
])

# Resultado del constructor
TreadResult = namedtuple('TreadResult', [
    'treads', 'risers', 'stringers', 'column',
    'tread_data', 'total_weight', 'summary'
])


class TreadProfileBuilder:
    """Construye perfiles de peldanos."""

    # Pesos por material (kg/m3)
    MATERIAL_DENSITY = {
        'steel': 7850,
        'wood': 700,
        'glass': 2500,
        'concrete': 2400,
        'aluminum': 2700
    }

    def __init__(self, material='steel'):
        self.material = material
        self.density = self.MATERIAL_DENSITY.get(material, 7850)

    def create_tread_profile(self, inner_radius, outer_radius,
                              angle_start, angle_end,
                              thickness, nosing=25):
        """
        Crea el perfil de un peldano en forma de sector.

        Args:
            inner_radius: Radio interior (mm)
            outer_radius: Radio exterior (mm)
            angle_start: Angulo inicial (radianes)
            angle_end: Angulo final (radianes)
            thickness: Espesor (mm)
            nosing: Proyeccion de nariz (mm)

        Returns:
            Curve: Perfil del peldano
        """
        # Agregar nosing al angulo
        nosing_angle = nosing / outer_radius

        # Puntos del perfil (sector con nariz)
        points = []

        # Arco exterior con nosing
        outer_r = outer_radius
        for i in range(9):
            t = i / 8
            a = (angle_start - nosing_angle) + t * (angle_end - angle_start + nosing_angle)
            x = outer_r * math.cos(a)
            y = outer_r * math.sin(a)
            points.append(rg.Point3d(x, y, 0))

        # Arco interior (sin nosing)
        for i in range(9):
            t = 1 - i / 8
            a = angle_start + t * (angle_end - angle_start)
            x = inner_radius * math.cos(a)
            y = inner_radius * math.sin(a)
            points.append(rg.Point3d(x, y, 0))

        points.append(points[0])  # Cerrar

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def create_tread_solid(self, profile, thickness, height):
        """
        Crea el solido del peldano.

        Args:
            profile: Curva de perfil
            thickness: Espesor (mm)
            height: Altura Z del peldano (mm)

        Returns:
            Brep: Solido del peldano
        """
        # Mover perfil a la altura
        transform = rg.Transform.Translation(0, 0, height)
        profile_at_height = profile.Duplicate()
        profile_at_height.Transform(transform)

        # Extruir hacia abajo
        extrusion = rg.Extrusion.Create(
            profile_at_height,
            -thickness,
            True  # Tapar
        )

        if extrusion:
            return extrusion.ToBrep()
        return None

    def calculate_weight(self, brep):
        """Calcula peso del peldano."""
        if brep is None:
            return 0

        props = rg.VolumeMassProperties.Compute(brep)
        if props:
            volume_m3 = props.Volume / 1e9  # mm3 a m3
            return volume_m3 * self.density
        return 0


class StructureBuilder:
    """Construye la estructura de soporte."""

    def __init__(self, structure_type='central_column'):
        """
        Args:
            structure_type: Tipo de estructura
        """
        self.structure_type = structure_type

    def build(self, spiral_data, column_diameter=150, column_thickness=6):
        """
        Construye la estructura de soporte.

        Args:
            spiral_data: Datos de la espiral
            column_diameter: Diametro de columna (mm)
            column_thickness: Espesor de pared (mm)

        Returns:
            List[Brep]: Elementos estructurales
        """
        if self.structure_type == 'central_column':
            return self._build_central_column(
                spiral_data, column_diameter, column_thickness
            )
        elif self.structure_type == 'perimeter_beam':
            return self._build_perimeter_beam(spiral_data)
        elif self.structure_type == 'double_stringer':
            return self._build_double_stringer(spiral_data)
        else:
            return self._build_central_column(
                spiral_data, column_diameter, column_thickness
            )

    def _build_central_column(self, spiral_data, diameter, thickness):
        """Construye columna central."""
        elements = []
        stats = spiral_data.geometry_stats
        height = stats['floor_to_floor']

        # Tubo exterior
        outer_circle = rg.Circle(rg.Plane.WorldXY, diameter / 2)
        outer_cylinder = rg.Extrusion.Create(
            outer_circle.ToNurbsCurve(),
            height,
            True
        )

        if outer_cylinder:
            elements.append(outer_cylinder.ToBrep())

        # Placa base
        base_diameter = diameter * 2.5
        base_thickness = 20
        base_circle = rg.Circle(
            rg.Plane.WorldXY,
            base_diameter / 2
        )
        base_plate = rg.Extrusion.Create(
            base_circle.ToNurbsCurve(),
            -base_thickness,
            True
        )
        if base_plate:
            elements.append(base_plate.ToBrep())

        # Placa superior
        top_plane = rg.Plane(rg.Point3d(0, 0, height), rg.Vector3d.ZAxis)
        top_circle = rg.Circle(top_plane, base_diameter / 2)
        top_plate = rg.Extrusion.Create(
            top_circle.ToNurbsCurve(),
            base_thickness,
            True
        )
        if top_plate:
            elements.append(top_plate.ToBrep())

        return elements

    def _build_perimeter_beam(self, spiral_data):
        """Construye viga helicoidal perimetral."""
        elements = []

        # Usar la curva exterior como guia
        outer_curve = spiral_data.outer_curve
        if outer_curve is None:
            return elements

        # Crear perfil de viga (rectangular)
        beam_width = 100
        beam_height = 150

        # Perfil en el plano perpendicular
        profile_plane = rg.Plane.WorldXY
        profile = rg.Rectangle3d(
            profile_plane,
            rg.Interval(-beam_width / 2, beam_width / 2),
            rg.Interval(-beam_height, 0)
        )

        # Obtener frame al inicio
        success, start_plane = outer_curve.PerpendicularFrameAt(
            outer_curve.Domain.T0
        )
        if success:
            transform = rg.Transform.PlaneToPlane(
                rg.Plane.WorldXY, start_plane
            )
            profile_curve = profile.ToNurbsCurve()
            profile_curve.Transform(transform)

            # Sweep
            sweep = rg.Brep.CreateFromSweep(
                outer_curve,
                profile_curve,
                True,  # Cerrado
                0.001
            )

            if sweep:
                elements.extend(sweep)

        return elements

    def _build_double_stringer(self, spiral_data):
        """Construye doble larguero (interior y exterior)."""
        elements = []

        # Larguero exterior
        outer_curve = spiral_data.outer_curve
        inner_curve = spiral_data.inner_curve

        stringer_width = 80
        stringer_height = 120

        for curve in [outer_curve, inner_curve]:
            if curve is None:
                continue

            profile = rg.Rectangle3d(
                rg.Plane.WorldXY,
                rg.Interval(-stringer_width / 2, stringer_width / 2),
                rg.Interval(-stringer_height, 0)
            )

            success, start_plane = curve.PerpendicularFrameAt(
                curve.Domain.T0
            )
            if success:
                transform = rg.Transform.PlaneToPlane(
                    rg.Plane.WorldXY, start_plane
                )
                profile_curve = profile.ToNurbsCurve()
                profile_curve.Transform(transform)

                sweep = rg.Brep.CreateFromSweep(
                    curve,
                    profile_curve,
                    True,
                    0.001
                )

                if sweep:
                    elements.extend(sweep)

        return elements


class RiserBuilder:
    """Construye contrahuellas."""

    def __init__(self, open_riser=True):
        self.open_riser = open_riser

    def build(self, spiral_data, tread_thickness):
        """
        Construye las contrahuellas.

        Args:
            spiral_data: Datos de la espiral
            tread_thickness: Espesor del peldano

        Returns:
            List[Brep]: Contrahuellas
        """
        if self.open_riser:
            return []

        risers = []
        stats = spiral_data.geometry_stats
        inner_radius = stats['inner_diameter'] / 2
        outer_radius = stats['outer_diameter'] / 2
        riser_height = stats['actual_riser']
        rotation_per_tread = stats['rotation_per_tread']

        for i in range(stats['tread_count']):
            tread_pos = spiral_data.tread_points[i]
            angle_rad = math.radians(tread_pos.angle)

            # Puntos de la contrahuella
            bottom_inner = rg.Point3d(
                inner_radius * math.cos(angle_rad),
                inner_radius * math.sin(angle_rad),
                tread_pos.height
            )
            bottom_outer = rg.Point3d(
                outer_radius * math.cos(angle_rad),
                outer_radius * math.sin(angle_rad),
                tread_pos.height
            )
            top_inner = rg.Point3d(
                inner_radius * math.cos(angle_rad),
                inner_radius * math.sin(angle_rad),
                tread_pos.height + riser_height - tread_thickness
            )
            top_outer = rg.Point3d(
                outer_radius * math.cos(angle_rad),
                outer_radius * math.sin(angle_rad),
                tread_pos.height + riser_height - tread_thickness
            )

            # Crear superficie
            surface = rg.NurbsSurface.CreateFromCorners(
                bottom_inner, bottom_outer, top_outer, top_inner
            )

            if surface:
                risers.append(surface.ToBrep())

        return risers


class TreadBuilder:
    """Constructor principal de peldanos."""

    def __init__(self, material='steel', structure_type='central_column'):
        self.material = material
        self.structure_type = structure_type
        self.profile_builder = TreadProfileBuilder(material)
        self.structure_builder = StructureBuilder(structure_type)

    def build(self, spiral_data, tread_thickness=40, nosing=25,
              open_riser=True, column_diameter=150):
        """
        Construye todos los peldanos y estructura.

        Args:
            spiral_data: Datos de la espiral
            tread_thickness: Espesor del peldano (mm)
            nosing: Proyeccion de nariz (mm)
            open_riser: Contrahuella abierta
            column_diameter: Diametro de columna (mm)

        Returns:
            TreadResult
        """
        treads = []
        tread_data = []
        total_weight = 0

        stats = spiral_data.geometry_stats
        inner_radius = stats['inner_diameter'] / 2
        outer_radius = stats['outer_diameter'] / 2
        rotation_per_tread = math.radians(stats['rotation_per_tread'])

        # Construir cada peldano
        for i, tread_pos in enumerate(spiral_data.tread_points[:-1]):  # Sin el ultimo (llegada)
            angle_start = math.radians(tread_pos.angle)
            angle_end = angle_start + rotation_per_tread

            # Crear perfil
            profile = self.profile_builder.create_tread_profile(
                inner_radius, outer_radius,
                angle_start, angle_end,
                tread_thickness, nosing
            )

            # Crear solido
            tread_brep = self.profile_builder.create_tread_solid(
                profile, tread_thickness, tread_pos.height
            )

            if tread_brep:
                treads.append(tread_brep)

                # Calcular peso
                weight = self.profile_builder.calculate_weight(tread_brep)
                total_weight += weight

                # Calcular area
                area_props = rg.AreaMassProperties.Compute(tread_brep)
                area = area_props.Area / 1e6 if area_props else 0  # mm2 a m2

                data = TreadGeometry(
                    index=i,
                    brep=tread_brep,
                    area=area,
                    inner_edge=profile,
                    outer_edge=None,
                    nosing_edge=None,
                    material=self.material,
                    weight=weight
                )
                tread_data.append(data)

        # Construir contrahuellas
        riser_builder = RiserBuilder(open_riser)
        risers = riser_builder.build(spiral_data, tread_thickness)

        # Construir estructura
        structure = self.structure_builder.build(
            spiral_data, column_diameter, 6
        )

        # Calcular peso de estructura (estimado)
        structure_weight = self._estimate_structure_weight(
            spiral_data, column_diameter
        )
        total_weight += structure_weight

        # Resumen
        summary = {
            'tread_count': len(treads),
            'total_weight': total_weight,
            'tread_weight': total_weight - structure_weight,
            'structure_weight': structure_weight,
            'material': self.material,
            'structure_type': self.structure_type,
            'avg_tread_area': sum(t.area for t in tread_data) / len(tread_data) if tread_data else 0
        }

        return TreadResult(
            treads=treads,
            risers=risers,
            stringers=[],
            column=structure,
            tread_data=tread_data,
            total_weight=total_weight,
            summary=summary
        )

    def _estimate_structure_weight(self, spiral_data, column_diameter):
        """Estima peso de la estructura."""
        stats = spiral_data.geometry_stats
        height = stats['floor_to_floor'] / 1000  # m

        if self.structure_type == 'central_column':
            # Tubo de acero
            diameter = column_diameter / 1000  # m
            thickness = 0.006  # 6mm
            area = math.pi * (diameter * thickness - thickness ** 2)
            volume = area * height
            weight = volume * 7850  # kg

            # Agregar placas base y superior
            weight += 20  # kg aproximado

            return weight

        elif self.structure_type == 'perimeter_beam':
            # Viga helicoidal
            helix_length = stats['helix_length'] / 1000  # m
            section_area = 0.1 * 0.15  # 100x150mm
            volume = section_area * helix_length
            return volume * 7850

        else:
            return 50  # Estimado por defecto


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    builder = TreadBuilder(
        material=tread_material if 'tread_material' in dir() else 'steel',
        structure_type=structure_type if 'structure_type' in dir() else 'central_column'
    )

    result = builder.build(
        spiral_data=spiral_data if 'spiral_data' in dir() else None,
        tread_thickness=tread_thickness if 'tread_thickness' in dir() else 40,
        nosing=nosing if 'nosing' in dir() else 25,
        open_riser=open_riser if 'open_riser' in dir() else True,
        column_diameter=column_diameter if 'column_diameter' in dir() else 150
    )

    # Salidas para Grasshopper
    treads = result.treads
    risers = result.risers
    structure = result.column
    tread_data = result.tread_data
    total_weight = result.total_weight
    summary = result.summary
