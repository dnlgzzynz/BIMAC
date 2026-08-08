#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diffuser Builder - M02 HVAC Modular
Generador de difusores de suministro y rejillas de retorno

Clases principales:
- DiffuserDatabase: Base de datos de tipos de difusores
- SquareDiffuserBuilder: Difusores cuadrados 4 vias
- LinearSlotBuilder: Difusores lineales tipo slot
- RoundDiffuserBuilder: Difusores circulares de techo
- ReturnGrilleBuilder: Rejillas de retorno
- DiffuserAssemblyBuilder: Ensamblaje completo de terminales
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
DiffuserGeometry = namedtuple('DiffuserGeometry', [
    'body', 'face_plate', 'damper', 'plenum_box', 'neck'
])

DiffuserSpecs = namedtuple('DiffuserSpecs', [
    'size', 'cfm_min', 'cfm_max', 'nc_rating', 'throw_ft', 'pressure_drop'
])

GrilleGeometry = namedtuple('GrilleGeometry', [
    'frame', 'blades', 'filter_frame', 'damper'
])


class DiffuserDatabase:
    """Base de datos de especificaciones de difusores."""

    # Difusores cuadrados 4 vias (pulgadas)
    SQUARE_4WAY = {
        '6x6': DiffuserSpecs((6, 6), 25, 85, 20, 4, 0.02),
        '8x8': DiffuserSpecs((8, 8), 50, 150, 22, 6, 0.03),
        '10x10': DiffuserSpecs((10, 10), 75, 250, 25, 8, 0.04),
        '12x12': DiffuserSpecs((12, 12), 100, 400, 28, 10, 0.05),
        '14x14': DiffuserSpecs((14, 14), 150, 550, 30, 12, 0.06),
        '16x16': DiffuserSpecs((16, 16), 200, 750, 32, 14, 0.07),
        '18x18': DiffuserSpecs((18, 18), 250, 950, 34, 16, 0.08),
        '24x24': DiffuserSpecs((24, 24), 400, 1400, 38, 20, 0.10),
    }

    # Difusores lineales slot (ancho en pulgadas, largo por pie)
    LINEAR_SLOT = {
        '1_slot': DiffuserSpecs((1, 48), 15, 45, 25, 8, 0.03),
        '2_slot': DiffuserSpecs((2, 48), 30, 90, 28, 12, 0.04),
        '3_slot': DiffuserSpecs((3, 48), 45, 135, 30, 16, 0.05),
        '4_slot': DiffuserSpecs((4, 48), 60, 180, 32, 20, 0.06),
    }

    # Difusores circulares de techo (diametro en pulgadas)
    ROUND_CEILING = {
        '6': DiffuserSpecs((6,), 25, 100, 20, 5, 0.02),
        '8': DiffuserSpecs((8,), 50, 175, 22, 7, 0.03),
        '10': DiffuserSpecs((10,), 75, 275, 25, 9, 0.04),
        '12': DiffuserSpecs((12,), 100, 400, 28, 11, 0.05),
        '14': DiffuserSpecs((14,), 150, 550, 30, 13, 0.06),
    }

    # Rejillas de retorno (pulgadas)
    RETURN_GRILLES = {
        '8x8': DiffuserSpecs((8, 8), 50, 200, 15, 0, 0.02),
        '10x10': DiffuserSpecs((10, 10), 100, 350, 18, 0, 0.03),
        '12x12': DiffuserSpecs((12, 12), 150, 500, 20, 0, 0.04),
        '14x14': DiffuserSpecs((14, 14), 200, 700, 22, 0, 0.05),
        '16x16': DiffuserSpecs((16, 16), 300, 950, 25, 0, 0.06),
        '18x18': DiffuserSpecs((18, 18), 400, 1200, 28, 0, 0.07),
        '24x24': DiffuserSpecs((24, 24), 600, 1800, 32, 0, 0.09),
        '12x6': DiffuserSpecs((12, 6), 75, 250, 18, 0, 0.03),
        '18x6': DiffuserSpecs((18, 6), 100, 350, 20, 0, 0.04),
        '24x6': DiffuserSpecs((24, 6), 150, 500, 22, 0, 0.05),
        '24x8': DiffuserSpecs((24, 8), 200, 650, 24, 0, 0.05),
        '36x8': DiffuserSpecs((36, 8), 300, 900, 26, 0, 0.06),
        '48x8': DiffuserSpecs((48, 8), 400, 1200, 28, 0, 0.07),
    }

    @classmethod
    def select_square_diffuser(cls, cfm):
        """Selecciona difusor cuadrado por CFM."""
        for size, specs in sorted(cls.SQUARE_4WAY.items(),
                                  key=lambda x: x[1].cfm_max):
            if specs.cfm_min <= cfm <= specs.cfm_max:
                return size, specs
        # Retornar el mas grande si excede
        return '24x24', cls.SQUARE_4WAY['24x24']

    @classmethod
    def select_round_diffuser(cls, cfm):
        """Selecciona difusor circular por CFM."""
        for size, specs in sorted(cls.ROUND_CEILING.items(),
                                  key=lambda x: x[1].cfm_max):
            if specs.cfm_min <= cfm <= specs.cfm_max:
                return size, specs
        return '14', cls.ROUND_CEILING['14']

    @classmethod
    def select_return_grille(cls, cfm):
        """Selecciona rejilla de retorno por CFM."""
        for size, specs in sorted(cls.RETURN_GRILLES.items(),
                                  key=lambda x: x[1].cfm_max):
            if specs.cfm_min <= cfm <= specs.cfm_max:
                return size, specs
        return '24x24', cls.RETURN_GRILLES['24x24']


class SquareDiffuserBuilder:
    """Constructor de difusores cuadrados 4 vias."""

    # Dimensiones estandar (mm)
    FACE_MARGIN = 25.0          # Margen del plafon
    FACE_THICKNESS = 2.0        # Espesor de placa frontal
    BODY_DEPTH = 150.0          # Profundidad del cuerpo
    NECK_HEIGHT = 100.0         # Altura del cuello
    PLENUM_HEIGHT = 200.0       # Altura de plenum box
    DAMPER_THICKNESS = 1.5      # Espesor de damper

    def __init__(self, size_inches, include_plenum=True):
        """
        Inicializa constructor de difusor cuadrado.

        Args:
            size_inches: Tupla (ancho, alto) en pulgadas
            include_plenum: Si incluir plenum box
        """
        self.width = size_inches[0] * 25.4  # Convertir a mm
        self.height = size_inches[1] * 25.4
        self.include_plenum = include_plenum

    def build_at_point(self, center_point, duct_diameter_mm=None):
        """
        Construye difusor en punto especificado.

        Args:
            center_point: Punto central en plafon
            duct_diameter_mm: Diametro de ducto de conexion

        Returns:
            DiffuserGeometry con todos los componentes
        """
        # Placa frontal (cara visible)
        face_plate = self._build_face_plate(center_point)

        # Cuerpo del difusor
        body = self._build_body(center_point)

        # Damper de control
        damper = self._build_damper(center_point)

        # Cuello de conexion
        neck_diameter = duct_diameter_mm or min(self.width, self.height) * 0.7
        neck = self._build_neck(center_point, neck_diameter)

        # Plenum box opcional
        plenum_box = None
        if self.include_plenum:
            plenum_box = self._build_plenum_box(center_point, neck_diameter)

        return DiffuserGeometry(
            body=body,
            face_plate=face_plate,
            damper=damper,
            plenum_box=plenum_box,
            neck=neck
        )

    def _build_face_plate(self, center):
        """Construye placa frontal decorativa."""
        # Rectangulo exterior con margen
        outer_width = self.width + 2 * self.FACE_MARGIN
        outer_height = self.height + 2 * self.FACE_MARGIN

        # Perfil rectangular
        corners = [
            rg.Point3d(center.X - outer_width/2, center.Y - outer_height/2, center.Z),
            rg.Point3d(center.X + outer_width/2, center.Y - outer_height/2, center.Z),
            rg.Point3d(center.X + outer_width/2, center.Y + outer_height/2, center.Z),
            rg.Point3d(center.X - outer_width/2, center.Y + outer_height/2, center.Z),
        ]

        outer_curve = rg.PolylineCurve([rg.Point3d(p.X, p.Y, p.Z) for p in corners + [corners[0]]])

        # Extruir hacia abajo
        extrusion_vector = rg.Vector3d(0, 0, -self.FACE_THICKNESS)
        face = rg.Extrusion.Create(outer_curve, -self.FACE_THICKNESS, True)

        return face.ToBrep() if face else None

    def _build_body(self, center):
        """Construye cuerpo del difusor con deflectores."""
        # Caja principal
        body_top = center.Z - self.FACE_THICKNESS

        # Perfil del cuerpo
        corners = [
            rg.Point3d(center.X - self.width/2, center.Y - self.height/2, body_top),
            rg.Point3d(center.X + self.width/2, center.Y - self.height/2, body_top),
            rg.Point3d(center.X + self.width/2, center.Y + self.height/2, body_top),
            rg.Point3d(center.X - self.width/2, center.Y + self.height/2, body_top),
        ]

        body_curve = rg.PolylineCurve([rg.Point3d(p.X, p.Y, p.Z) for p in corners + [corners[0]]])

        # Extruir cuerpo
        body = rg.Extrusion.Create(body_curve, self.BODY_DEPTH, True)

        return body.ToBrep() if body else None

    def _build_damper(self, center):
        """Construye damper de control de flujo."""
        damper_z = center.Z + self.BODY_DEPTH * 0.7
        damper_size = min(self.width, self.height) * 0.6

        # Placa circular del damper
        damper_circle = rg.Circle(
            rg.Plane(rg.Point3d(center.X, center.Y, damper_z), rg.Vector3d.ZAxis),
            damper_size / 2
        )

        disk = rg.Extrusion.CreateCylinderExtrusion(
            damper_circle.Radius,
            self.DAMPER_THICKNESS,
            True,
            True
        )

        if disk:
            disk_brep = disk.ToBrep()
            xform = rg.Transform.Translation(center.X, center.Y, damper_z)
            disk_brep.Transform(xform)
            return disk_brep

        return None

    def _build_neck(self, center, diameter):
        """Construye cuello de conexion a ducto."""
        neck_bottom = center.Z + self.BODY_DEPTH

        # Cuello circular
        neck_circle = rg.Circle(
            rg.Plane(rg.Point3d(center.X, center.Y, neck_bottom), rg.Vector3d.ZAxis),
            diameter / 2
        )

        cylinder = rg.Cylinder(neck_circle, self.NECK_HEIGHT)

        return cylinder.ToBrep(True, True)

    def _build_plenum_box(self, center, neck_diameter):
        """Construye plenum box de conexion."""
        plenum_bottom = center.Z + self.BODY_DEPTH + self.NECK_HEIGHT
        plenum_size = max(self.width, self.height) * 1.2

        corners = [
            rg.Point3d(center.X - plenum_size/2, center.Y - plenum_size/2, plenum_bottom),
            rg.Point3d(center.X + plenum_size/2, center.Y - plenum_size/2, plenum_bottom),
            rg.Point3d(center.X + plenum_size/2, center.Y + plenum_size/2, plenum_bottom),
            rg.Point3d(center.X - plenum_size/2, center.Y + plenum_size/2, plenum_bottom),
        ]

        plenum_curve = rg.PolylineCurve([rg.Point3d(p.X, p.Y, p.Z) for p in corners + [corners[0]]])

        plenum = rg.Extrusion.Create(plenum_curve, self.PLENUM_HEIGHT, True)

        return plenum.ToBrep() if plenum else None


class LinearSlotBuilder:
    """Constructor de difusores lineales tipo slot."""

    # Dimensiones estandar (mm)
    SLOT_WIDTH = 25.0           # Ancho de cada slot
    SLOT_SPACING = 50.0         # Espaciado entre slots
    FRAME_WIDTH = 35.0          # Ancho del marco
    FRAME_DEPTH = 150.0         # Profundidad del marco
    PLENUM_HEIGHT = 200.0       # Altura del plenum

    def __init__(self, num_slots, length_mm):
        """
        Inicializa constructor de difusor lineal.

        Args:
            num_slots: Numero de slots (1-4)
            length_mm: Longitud total en mm
        """
        self.num_slots = min(4, max(1, num_slots))
        self.length = length_mm
        self.total_width = (self.num_slots * self.SLOT_WIDTH +
                           (self.num_slots - 1) * self.SLOT_SPACING +
                           2 * self.FRAME_WIDTH)

    def build_at_line(self, start_point, end_point):
        """
        Construye difusor lineal entre dos puntos.

        Args:
            start_point: Punto inicial
            end_point: Punto final

        Returns:
            DiffuserGeometry con componentes
        """
        # Vector de direccion
        direction = rg.Vector3d(end_point - start_point)
        direction.Unitize()

        # Vector perpendicular
        perp = rg.Vector3d.CrossProduct(direction, rg.Vector3d.ZAxis)
        perp.Unitize()

        # Centro
        center = rg.Point3d(
            (start_point.X + end_point.X) / 2,
            (start_point.Y + end_point.Y) / 2,
            (start_point.Z + end_point.Z) / 2
        )

        # Longitud real
        actual_length = start_point.DistanceTo(end_point)

        # Construir marco
        frame = self._build_frame(center, direction, perp, actual_length)

        # Construir slots
        slots = self._build_slots(center, direction, perp, actual_length)

        # Plenum
        plenum = self._build_plenum(center, direction, perp, actual_length)

        return DiffuserGeometry(
            body=frame,
            face_plate=slots,
            damper=None,
            plenum_box=plenum,
            neck=None
        )

    def _build_frame(self, center, direction, perp, length):
        """Construye marco del difusor lineal."""
        # Esquinas del marco
        half_length = length / 2
        half_width = self.total_width / 2

        corners = [
            center + direction * half_length + perp * half_width,
            center + direction * half_length - perp * half_width,
            center - direction * half_length - perp * half_width,
            center - direction * half_length + perp * half_width,
        ]

        frame_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
        frame = rg.Extrusion.Create(frame_curve, self.FRAME_DEPTH, True)

        return frame.ToBrep() if frame else None

    def _build_slots(self, center, direction, perp, length):
        """Construye aberturas de slots."""
        slots = []
        half_length = length / 2 - self.FRAME_WIDTH

        # Posicion inicial de slots
        start_offset = -(self.num_slots - 1) * (self.SLOT_WIDTH + self.SLOT_SPACING) / 2

        for i in range(self.num_slots):
            slot_offset = start_offset + i * (self.SLOT_WIDTH + self.SLOT_SPACING)
            slot_center = center + perp * slot_offset

            corners = [
                slot_center + direction * half_length + perp * (self.SLOT_WIDTH/2),
                slot_center + direction * half_length - perp * (self.SLOT_WIDTH/2),
                slot_center - direction * half_length - perp * (self.SLOT_WIDTH/2),
                slot_center - direction * half_length + perp * (self.SLOT_WIDTH/2),
            ]

            slot_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
            slot = rg.Extrusion.Create(slot_curve, -10.0, True)

            if slot:
                slots.append(slot.ToBrep())

        return slots if slots else None

    def _build_plenum(self, center, direction, perp, length):
        """Construye plenum del difusor lineal."""
        plenum_center = rg.Point3d(center.X, center.Y, center.Z + self.FRAME_DEPTH)
        half_length = length / 2
        half_width = self.total_width / 2

        corners = [
            plenum_center + direction * half_length + perp * half_width,
            plenum_center + direction * half_length - perp * half_width,
            plenum_center - direction * half_length - perp * half_width,
            plenum_center - direction * half_length + perp * half_width,
        ]

        plenum_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
        plenum = rg.Extrusion.Create(plenum_curve, self.PLENUM_HEIGHT, True)

        return plenum.ToBrep() if plenum else None


class RoundDiffuserBuilder:
    """Constructor de difusores circulares de techo."""

    # Dimensiones estandar (mm)
    FACE_MARGIN = 20.0          # Margen del plafon
    FACE_THICKNESS = 2.0        # Espesor de placa
    CONE_DEPTH = 80.0           # Profundidad del cono
    NECK_HEIGHT = 100.0         # Altura del cuello

    def __init__(self, diameter_inches):
        """
        Inicializa constructor de difusor circular.

        Args:
            diameter_inches: Diametro en pulgadas
        """
        self.diameter = diameter_inches * 25.4  # Convertir a mm

    def build_at_point(self, center_point, pattern='radial'):
        """
        Construye difusor circular en punto.

        Args:
            center_point: Punto central
            pattern: Patron de difusion ('radial', 'adjustable', 'perforated')

        Returns:
            DiffuserGeometry
        """
        # Placa frontal circular
        face_plate = self._build_face_plate(center_point)

        # Cuerpo conico
        body = self._build_cone_body(center_point)

        # Cuello de conexion
        neck = self._build_neck(center_point)

        # Cono difusor (parte visible)
        diffuser_cone = self._build_diffuser_cone(center_point, pattern)

        return DiffuserGeometry(
            body=body,
            face_plate=face_plate,
            damper=diffuser_cone,
            plenum_box=None,
            neck=neck
        )

    def _build_face_plate(self, center):
        """Construye placa frontal circular."""
        outer_radius = self.diameter / 2 + self.FACE_MARGIN

        circle = rg.Circle(
            rg.Plane(center, rg.Vector3d.ZAxis),
            outer_radius
        )

        cylinder = rg.Cylinder(circle, -self.FACE_THICKNESS)

        return cylinder.ToBrep(True, True)

    def _build_cone_body(self, center):
        """Construye cuerpo conico del difusor."""
        # Circulo inferior (cara)
        bottom_z = center.Z - self.FACE_THICKNESS
        bottom_circle = rg.Circle(
            rg.Plane(rg.Point3d(center.X, center.Y, bottom_z), rg.Vector3d.ZAxis),
            self.diameter / 2
        )

        # Circulo superior (cuello)
        top_z = bottom_z + self.CONE_DEPTH
        neck_radius = self.diameter / 2 * 0.6
        top_circle = rg.Circle(
            rg.Plane(rg.Point3d(center.X, center.Y, top_z), rg.Vector3d.ZAxis),
            neck_radius
        )

        # Loft entre circulos
        bottom_curve = bottom_circle.ToNurbsCurve()
        top_curve = top_circle.ToNurbsCurve()

        loft = rg.Brep.CreateFromLoft(
            [bottom_curve, top_curve],
            rg.Point3d.Unset,
            rg.Point3d.Unset,
            rg.LoftType.Normal,
            False
        )

        return loft[0] if loft else None

    def _build_neck(self, center):
        """Construye cuello de conexion."""
        neck_z = center.Z - self.FACE_THICKNESS + self.CONE_DEPTH
        neck_radius = self.diameter / 2 * 0.6

        circle = rg.Circle(
            rg.Plane(rg.Point3d(center.X, center.Y, neck_z), rg.Vector3d.ZAxis),
            neck_radius
        )

        cylinder = rg.Cylinder(circle, self.NECK_HEIGHT)

        return cylinder.ToBrep(True, True)

    def _build_diffuser_cone(self, center, pattern):
        """Construye cono difusor central."""
        cone_base_z = center.Z - self.FACE_THICKNESS * 0.5
        cone_radius = self.diameter / 2 * 0.4
        cone_height = self.CONE_DEPTH * 0.5

        # Cono central
        base_plane = rg.Plane(
            rg.Point3d(center.X, center.Y, cone_base_z),
            rg.Vector3d.ZAxis
        )

        cone = rg.Cone(base_plane, cone_height, cone_radius)

        return cone.ToBrep(True)


class ReturnGrilleBuilder:
    """Constructor de rejillas de retorno."""

    # Dimensiones estandar (mm)
    FRAME_WIDTH = 25.0          # Ancho del marco
    FRAME_DEPTH = 50.0          # Profundidad del marco
    BLADE_THICKNESS = 1.5       # Espesor de aleta
    BLADE_SPACING = 15.0        # Espaciado de aletas
    BLADE_ANGLE = 45.0          # Angulo de aletas (grados)

    def __init__(self, width_inches, height_inches, with_filter=False):
        """
        Inicializa constructor de rejilla.

        Args:
            width_inches: Ancho en pulgadas
            height_inches: Alto en pulgadas
            with_filter: Si incluir marco para filtro
        """
        self.width = width_inches * 25.4
        self.height = height_inches * 25.4
        self.with_filter = with_filter

    def build_at_point(self, center_point, blade_direction='horizontal'):
        """
        Construye rejilla en punto especificado.

        Args:
            center_point: Punto central
            blade_direction: Direccion de aletas ('horizontal', 'vertical')

        Returns:
            GrilleGeometry
        """
        # Marco exterior
        frame = self._build_frame(center_point)

        # Aletas
        blades = self._build_blades(center_point, blade_direction)

        # Marco de filtro opcional
        filter_frame = None
        if self.with_filter:
            filter_frame = self._build_filter_frame(center_point)

        # Damper opcional
        damper = self._build_damper(center_point)

        return GrilleGeometry(
            frame=frame,
            blades=blades,
            filter_frame=filter_frame,
            damper=damper
        )

    def _build_frame(self, center):
        """Construye marco de la rejilla."""
        # Perfil exterior
        outer_w = self.width / 2 + self.FRAME_WIDTH
        outer_h = self.height / 2 + self.FRAME_WIDTH

        outer_corners = [
            rg.Point3d(center.X - outer_w, center.Y - outer_h, center.Z),
            rg.Point3d(center.X + outer_w, center.Y - outer_h, center.Z),
            rg.Point3d(center.X + outer_w, center.Y + outer_h, center.Z),
            rg.Point3d(center.X - outer_w, center.Y + outer_h, center.Z),
        ]

        outer_curve = rg.PolylineCurve([p for p in outer_corners + [outer_corners[0]]])

        # Perfil interior
        inner_w = self.width / 2
        inner_h = self.height / 2

        inner_corners = [
            rg.Point3d(center.X - inner_w, center.Y - inner_h, center.Z),
            rg.Point3d(center.X + inner_w, center.Y - inner_h, center.Z),
            rg.Point3d(center.X + inner_w, center.Y + inner_h, center.Z),
            rg.Point3d(center.X - inner_w, center.Y + inner_h, center.Z),
        ]

        inner_curve = rg.PolylineCurve([p for p in inner_corners + [inner_corners[0]]])

        # Extruir marco
        outer_extrusion = rg.Extrusion.Create(outer_curve, self.FRAME_DEPTH, True)

        return outer_extrusion.ToBrep() if outer_extrusion else None

    def _build_blades(self, center, direction):
        """Construye aletas de la rejilla."""
        blades = []

        if direction == 'horizontal':
            # Aletas horizontales
            blade_length = self.width - 10.0
            num_blades = int(self.height / self.BLADE_SPACING)
            start_y = center.Y - (num_blades - 1) * self.BLADE_SPACING / 2

            for i in range(num_blades):
                blade_y = start_y + i * self.BLADE_SPACING
                blade = self._create_single_blade(
                    center.X, blade_y, center.Z,
                    blade_length, self.BLADE_SPACING * 0.8,
                    'horizontal'
                )
                if blade:
                    blades.append(blade)
        else:
            # Aletas verticales
            blade_length = self.height - 10.0
            num_blades = int(self.width / self.BLADE_SPACING)
            start_x = center.X - (num_blades - 1) * self.BLADE_SPACING / 2

            for i in range(num_blades):
                blade_x = start_x + i * self.BLADE_SPACING
                blade = self._create_single_blade(
                    blade_x, center.Y, center.Z,
                    blade_length, self.BLADE_SPACING * 0.8,
                    'vertical'
                )
                if blade:
                    blades.append(blade)

        return blades

    def _create_single_blade(self, x, y, z, length, width, orientation):
        """Crea una aleta individual."""
        # Perfil de la aleta
        angle_rad = math.radians(self.BLADE_ANGLE)
        blade_depth = width * math.sin(angle_rad)

        if orientation == 'horizontal':
            corners = [
                rg.Point3d(x - length/2, y, z),
                rg.Point3d(x + length/2, y, z),
                rg.Point3d(x + length/2, y, z + blade_depth),
                rg.Point3d(x - length/2, y, z + blade_depth),
            ]
        else:
            corners = [
                rg.Point3d(x, y - length/2, z),
                rg.Point3d(x, y + length/2, z),
                rg.Point3d(x, y + length/2, z + blade_depth),
                rg.Point3d(x, y - length/2, z + blade_depth),
            ]

        blade_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
        blade = rg.Extrusion.Create(blade_curve, self.BLADE_THICKNESS, True)

        return blade.ToBrep() if blade else None

    def _build_filter_frame(self, center):
        """Construye marco para filtro."""
        filter_z = center.Z + self.FRAME_DEPTH + 25.0
        filter_depth = 50.0

        # Marco ligeramente mas pequeno
        margin = 10.0
        corners = [
            rg.Point3d(center.X - self.width/2 + margin,
                      center.Y - self.height/2 + margin, filter_z),
            rg.Point3d(center.X + self.width/2 - margin,
                      center.Y - self.height/2 + margin, filter_z),
            rg.Point3d(center.X + self.width/2 - margin,
                      center.Y + self.height/2 - margin, filter_z),
            rg.Point3d(center.X - self.width/2 + margin,
                      center.Y + self.height/2 - margin, filter_z),
        ]

        filter_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
        filter_frame = rg.Extrusion.Create(filter_curve, filter_depth, True)

        return filter_frame.ToBrep() if filter_frame else None

    def _build_damper(self, center):
        """Construye damper de control."""
        damper_z = center.Z + self.FRAME_DEPTH * 0.5
        damper_size = min(self.width, self.height) * 0.7

        corners = [
            rg.Point3d(center.X - damper_size/2, center.Y - damper_size/2, damper_z),
            rg.Point3d(center.X + damper_size/2, center.Y - damper_size/2, damper_z),
            rg.Point3d(center.X + damper_size/2, center.Y + damper_size/2, damper_z),
            rg.Point3d(center.X - damper_size/2, center.Y + damper_size/2, damper_z),
        ]

        damper_curve = rg.PolylineCurve([p for p in corners + [corners[0]]])
        damper = rg.Extrusion.Create(damper_curve, 2.0, True)

        return damper.ToBrep() if damper else None


class DiffuserAssemblyBuilder:
    """Ensamblador de multiples difusores en zona."""

    def __init__(self, zone_cfm, zone_area_m2, diffuser_type='square'):
        """
        Inicializa ensamblador de difusores.

        Args:
            zone_cfm: CFM total de la zona
            zone_area_m2: Area de la zona en m2
            diffuser_type: Tipo de difusor ('square', 'round', 'linear')
        """
        self.zone_cfm = zone_cfm
        self.zone_area = zone_area_m2
        self.diffuser_type = diffuser_type

        # Calcular numero de difusores
        self.cfm_per_diffuser = self._calculate_cfm_per_diffuser()
        self.num_diffusers = max(1, int(round(zone_cfm / self.cfm_per_diffuser)))

    def _calculate_cfm_per_diffuser(self):
        """Calcula CFM optimo por difusor."""
        # Basado en area tipica de cobertura
        coverage_m2 = 15.0  # m2 por difusor tipico

        if self.zone_area <= coverage_m2:
            return self.zone_cfm

        num_needed = max(1, int(self.zone_area / coverage_m2))
        return self.zone_cfm / num_needed

    def build_grid_layout(self, zone_boundary, ceiling_height):
        """
        Genera layout de difusores en grid.

        Args:
            zone_boundary: Curva del perimetro de zona
            ceiling_height: Altura de plafon

        Returns:
            Lista de DiffuserGeometry
        """
        # Obtener bounding box
        bbox = zone_boundary.GetBoundingBox(True)

        # Calcular grid
        zone_width = bbox.Max.X - bbox.Min.X
        zone_length = bbox.Max.Y - bbox.Min.Y

        # Numero de filas y columnas
        aspect = zone_length / zone_width if zone_width > 0 else 1.0
        cols = max(1, int(math.sqrt(self.num_diffusers / aspect)))
        rows = max(1, int(math.ceil(self.num_diffusers / cols)))

        # Espaciado
        spacing_x = zone_width / (cols + 1)
        spacing_y = zone_length / (rows + 1)

        # Generar puntos
        diffusers = []
        count = 0

        for row in range(rows):
            for col in range(cols):
                if count >= self.num_diffusers:
                    break

                x = bbox.Min.X + spacing_x * (col + 1)
                y = bbox.Min.Y + spacing_y * (row + 1)
                z = ceiling_height

                point = rg.Point3d(x, y, z)

                # Verificar que el punto esta dentro de la zona
                if self._point_in_boundary(point, zone_boundary):
                    # Seleccionar tamano de difusor
                    cfm = self.zone_cfm / self.num_diffusers

                    if self.diffuser_type == 'square':
                        size, specs = DiffuserDatabase.select_square_diffuser(cfm)
                        size_tuple = specs.size
                        builder = SquareDiffuserBuilder(size_tuple)
                        diffuser = builder.build_at_point(point)
                    elif self.diffuser_type == 'round':
                        size, specs = DiffuserDatabase.select_round_diffuser(cfm)
                        builder = RoundDiffuserBuilder(int(size))
                        diffuser = builder.build_at_point(point)
                    else:
                        # Default a cuadrado
                        size, specs = DiffuserDatabase.select_square_diffuser(cfm)
                        builder = SquareDiffuserBuilder(specs.size)
                        diffuser = builder.build_at_point(point)

                    diffusers.append(diffuser)
                    count += 1

            if count >= self.num_diffusers:
                break

        return diffusers

    def _point_in_boundary(self, point, boundary):
        """Verifica si punto esta dentro del boundary."""
        test_point = rg.Point3d(point.X, point.Y, boundary.PointAtStart.Z)
        result = boundary.Contains(test_point, rg.Plane.WorldXY, 0.001)
        return result == rg.PointContainment.Inside


class TerminalScheduleGenerator:
    """Generador de schedules de terminales HVAC."""

    def __init__(self):
        """Inicializa generador de schedules."""
        self.terminals = []

    def add_supply_diffuser(self, tag, diffuser_type, size, cfm, location):
        """Agrega difusor de suministro al schedule."""
        self.terminals.append({
            'tag': tag,
            'type': 'SUPPLY',
            'subtype': diffuser_type,
            'size': size,
            'cfm': cfm,
            'location': location
        })

    def add_return_grille(self, tag, size, cfm, location, has_filter=False):
        """Agrega rejilla de retorno al schedule."""
        self.terminals.append({
            'tag': tag,
            'type': 'RETURN',
            'subtype': 'GRILLE',
            'size': size,
            'cfm': cfm,
            'location': location,
            'filter': has_filter
        })

    def generate_schedule(self):
        """
        Genera schedule en formato tabla.

        Returns:
            Lista de diccionarios con datos del schedule
        """
        schedule = []

        for terminal in self.terminals:
            entry = {
                'TAG': terminal['tag'],
                'TYPE': terminal['type'],
                'DESCRIPTION': f"{terminal['subtype']} {terminal['size']}",
                'CFM': terminal['cfm'],
                'LOCATION': terminal['location']
            }

            if terminal.get('filter'):
                entry['NOTES'] = 'With Filter'

            schedule.append(entry)

        return schedule

    def get_totals(self):
        """Obtiene totales del schedule."""
        supply_cfm = sum(t['cfm'] for t in self.terminals if t['type'] == 'SUPPLY')
        return_cfm = sum(t['cfm'] for t in self.terminals if t['type'] == 'RETURN')

        return {
            'total_supply_cfm': supply_cfm,
            'total_return_cfm': return_cfm,
            'supply_count': len([t for t in self.terminals if t['type'] == 'SUPPLY']),
            'return_count': len([t for t in self.terminals if t['type'] == 'RETURN'])
        }
