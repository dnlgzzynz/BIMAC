#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de Helice - C02 Rampa Vehicular Helicoidal

Genera la geometria base de rampas helicoidales incluyendo
superficies de rodamiento, bordes y transiciones.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
HelixGeometry = namedtuple('HelixGeometry', [
    'inner_helix', 'outer_helix', 'centerline',
    'surface', 'start_angle', 'end_angle',
    'total_rise', 'total_length', 'slope'
])

RampSection = namedtuple('RampSection', [
    'angle', 'inner_point', 'outer_point', 'center_point',
    'elevation', 'superelevation', 'width'
])

TransitionGeometry = namedtuple('TransitionGeometry', [
    'entry_surface', 'exit_surface', 'entry_curve', 'exit_curve'
])


class HelixCurveGenerator:
    """Genera curvas helicoidales base."""

    def __init__(self, inner_radius, outer_radius, rise_per_turn,
                 total_turns, direction='clockwise'):
        """
        Args:
            inner_radius: Radio interior en metros
            outer_radius: Radio exterior en metros
            rise_per_turn: Altura por vuelta completa
            total_turns: Numero de vueltas (puede ser decimal)
            direction: 'clockwise' o 'counterclockwise'
        """
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.rise_per_turn = rise_per_turn
        self.total_turns = total_turns
        self.direction = direction

        # Calcular parametros derivados
        self.total_rise = rise_per_turn * total_turns
        self.total_angle = 2 * math.pi * total_turns
        self.center_radius = (inner_radius + outer_radius) / 2.0
        self.width = outer_radius - inner_radius

    def generate_helix_points(self, radius, point_count=100):
        """
        Genera puntos de una helice.

        Args:
            radius: Radio de la helice
            point_count: Numero de puntos

        Returns:
            list: Lista de Point3d
        """
        points = []
        direction_factor = 1 if self.direction == 'counterclockwise' else -1

        for i in range(point_count + 1):
            t = i / float(point_count)
            angle = t * self.total_angle * direction_factor

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = t * self.total_rise

            points.append(rg.Point3d(x, y, z))

        return points

    def generate_helix_curve(self, radius, degree=3):
        """
        Genera curva NURBS helicoidal.

        Args:
            radius: Radio de la helice
            degree: Grado de la curva NURBS

        Returns:
            NurbsCurve: Curva helicoidal
        """
        points = self.generate_helix_points(radius, point_count=100)
        curve = rg.NurbsCurve.Create(False, degree, points)
        return curve

    def generate_inner_helix(self):
        """Genera helice interior."""
        return self.generate_helix_curve(self.inner_radius)

    def generate_outer_helix(self):
        """Genera helice exterior."""
        return self.generate_helix_curve(self.outer_radius)

    def generate_centerline(self):
        """Genera linea central de la rampa."""
        return self.generate_helix_curve(self.center_radius)

    def calculate_slope(self):
        """
        Calcula pendiente de la rampa.

        Returns:
            float: Pendiente en porcentaje
        """
        # Longitud desarrollada en el centro
        center_length = 2 * math.pi * self.center_radius * self.total_turns

        # Pendiente
        slope = (self.total_rise / center_length) * 100

        return slope

    def calculate_arc_length(self, radius):
        """Calcula longitud de arco para un radio dado."""
        return 2 * math.pi * radius * self.total_turns

    def get_geometry(self):
        """
        Obtiene geometria completa de la helice.

        Returns:
            HelixGeometry: Geometria de la rampa
        """
        inner = self.generate_inner_helix()
        outer = self.generate_outer_helix()
        center = self.generate_centerline()

        # Crear superficie loft
        curves = [inner, outer]
        loft = rg.Brep.CreateFromLoft(
            curves, rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal, False
        )

        surface = loft[0] if loft else None

        return HelixGeometry(
            inner_helix=inner,
            outer_helix=outer,
            centerline=center,
            surface=surface,
            start_angle=0,
            end_angle=self.total_angle,
            total_rise=self.total_rise,
            total_length=self.calculate_arc_length(self.center_radius),
            slope=self.calculate_slope()
        )


class SuperelevationCalculator:
    """Calcula peralte (superelevation) variable."""

    def __init__(self, max_superelevation=4.0, transition_length=6.0):
        """
        Args:
            max_superelevation: Peralte maximo en porcentaje
            transition_length: Longitud de transicion en metros
        """
        self.max_super = max_superelevation / 100.0
        self.transition_length = transition_length

    def calculate_at_position(self, arc_length, total_length, is_entry=True):
        """
        Calcula peralte en una posicion dada.

        Args:
            arc_length: Distancia desde el inicio
            total_length: Longitud total de la rampa
            is_entry: Si esta en zona de entrada

        Returns:
            float: Peralte (ratio, no porcentaje)
        """
        # En zonas de transicion
        if arc_length < self.transition_length:
            # Transicion de entrada
            t = arc_length / self.transition_length
            return self.max_super * self._ease_in_out(t)

        elif arc_length > total_length - self.transition_length:
            # Transicion de salida
            remaining = total_length - arc_length
            t = remaining / self.transition_length
            return self.max_super * self._ease_in_out(t)

        else:
            # Zona de peralte constante
            return self.max_super

    def _ease_in_out(self, t):
        """Funcion de interpolacion suave."""
        return t * t * (3 - 2 * t)


class RampSurfaceBuilder:
    """Construye superficie de rodamiento con peralte."""

    def __init__(self, helix_generator, superelevation_calc):
        """
        Args:
            helix_generator: HelixCurveGenerator
            superelevation_calc: SuperelevationCalculator
        """
        self.helix = helix_generator
        self.super_calc = superelevation_calc

    def generate_sections(self, section_count=50):
        """
        Genera secciones transversales de la rampa.

        Args:
            section_count: Numero de secciones

        Returns:
            list: Lista de RampSection
        """
        sections = []
        total_length = self.helix.calculate_arc_length(self.helix.center_radius)
        direction_factor = 1 if self.helix.direction == 'counterclockwise' else -1

        for i in range(section_count + 1):
            t = i / float(section_count)

            # Angulo y elevacion
            angle = t * self.helix.total_angle * direction_factor
            elevation = t * self.helix.total_rise

            # Posicion en arco
            arc_length = t * total_length

            # Peralte
            super_ratio = self.super_calc.calculate_at_position(
                arc_length, total_length
            )

            # Puntos en planta
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            inner_pt = rg.Point3d(
                self.helix.inner_radius * cos_a,
                self.helix.inner_radius * sin_a,
                elevation
            )

            outer_pt = rg.Point3d(
                self.helix.outer_radius * cos_a,
                self.helix.outer_radius * sin_a,
                elevation
            )

            center_pt = rg.Point3d(
                self.helix.center_radius * cos_a,
                self.helix.center_radius * sin_a,
                elevation
            )

            # Aplicar peralte (elevar borde exterior)
            rise = self.helix.width * super_ratio
            outer_pt = rg.Point3d(outer_pt.X, outer_pt.Y, outer_pt.Z + rise)

            sections.append(RampSection(
                angle=angle,
                inner_point=inner_pt,
                outer_point=outer_pt,
                center_point=center_pt,
                elevation=elevation,
                superelevation=super_ratio * 100,
                width=self.helix.width
            ))

        return sections

    def build_surface(self, sections):
        """
        Construye superficie a partir de secciones.

        Args:
            sections: Lista de RampSection

        Returns:
            Brep: Superficie de la rampa
        """
        # Crear curvas de seccion
        section_curves = []

        for section in sections:
            line = rg.LineCurve(section.inner_point, section.outer_point)
            section_curves.append(line)

        # Loft entre secciones
        loft = rg.Brep.CreateFromLoft(
            section_curves, rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal, False
        )

        return loft[0] if loft else None

    def build_slab_solid(self, sections, thickness=0.25):
        """
        Construye solido de losa con espesor.

        Args:
            sections: Lista de RampSection
            thickness: Espesor de losa en metros

        Returns:
            Brep: Solido de la losa
        """
        # Superficie superior
        top_surface = self.build_surface(sections)

        if not top_surface:
            return None

        # Crear secciones inferiores (con offset hacia abajo)
        bottom_sections = []
        for section in sections:
            inner_bottom = rg.Point3d(
                section.inner_point.X,
                section.inner_point.Y,
                section.inner_point.Z - thickness
            )
            outer_bottom = rg.Point3d(
                section.outer_point.X,
                section.outer_point.Y,
                section.outer_point.Z - thickness
            )

            bottom_sections.append(RampSection(
                angle=section.angle,
                inner_point=inner_bottom,
                outer_point=outer_bottom,
                center_point=section.center_point,
                elevation=section.elevation - thickness,
                superelevation=section.superelevation,
                width=section.width
            ))

        # Superficie inferior
        bottom_surface = self.build_surface(bottom_sections)

        if not bottom_surface:
            return top_surface

        # Crear bordes
        edge_surfaces = self._create_edge_surfaces(sections, bottom_sections)

        # Unir todo
        all_surfaces = [top_surface, bottom_surface] + edge_surfaces
        joined = rg.Brep.JoinBreps(all_surfaces, 0.001)

        if joined and len(joined) > 0:
            # Intentar cerrar el solido
            if joined[0].IsSolid:
                return joined[0]
            else:
                # Capear extremos
                capped = joined[0].CapPlanarHoles(0.001)
                return capped if capped else joined[0]

        return top_surface

    def _create_edge_surfaces(self, top_sections, bottom_sections):
        """Crea superficies de borde."""
        edges = []

        # Borde interior
        inner_top_pts = [s.inner_point for s in top_sections]
        inner_bottom_pts = [s.inner_point for s in bottom_sections]

        inner_top = rg.NurbsCurve.Create(False, 3, inner_top_pts)
        inner_bottom = rg.NurbsCurve.Create(False, 3, inner_bottom_pts)

        if inner_top and inner_bottom:
            loft = rg.Brep.CreateFromLoft(
                [inner_top, inner_bottom], rg.Point3d.Unset, rg.Point3d.Unset,
                rg.LoftType.Normal, False
            )
            if loft:
                edges.append(loft[0])

        # Borde exterior
        outer_top_pts = [s.outer_point for s in top_sections]
        outer_bottom_pts = [s.outer_point for s in bottom_sections]

        outer_top = rg.NurbsCurve.Create(False, 3, outer_top_pts)
        outer_bottom = rg.NurbsCurve.Create(False, 3, outer_bottom_pts)

        if outer_top and outer_bottom:
            loft = rg.Brep.CreateFromLoft(
                [outer_top, outer_bottom], rg.Point3d.Unset, rg.Point3d.Unset,
                rg.LoftType.Normal, False
            )
            if loft:
                edges.append(loft[0])

        return edges


class TransitionBuilder:
    """Construye transiciones de entrada y salida."""

    def __init__(self, ramp_width, transition_length=10.0):
        """
        Args:
            ramp_width: Ancho de la rampa
            transition_length: Longitud de transicion
        """
        self.width = ramp_width
        self.length = transition_length

    def build_entry_transition(self, start_point, start_direction,
                                entry_width=None, entry_slope=0):
        """
        Construye transicion de entrada.

        Args:
            start_point: Punto de inicio de la rampa
            start_direction: Direccion tangente
            entry_width: Ancho de entrada (default = ancho rampa)
            entry_slope: Pendiente de entrada

        Returns:
            Brep: Superficie de transicion
        """
        if entry_width is None:
            entry_width = self.width

        # Normalizar direccion
        direction = rg.Vector3d(start_direction)
        direction.Unitize()

        # Direccion lateral
        lateral = rg.Vector3d.CrossProduct(direction, rg.Vector3d.ZAxis)
        lateral.Unitize()

        # Puntos de entrada (antes de la rampa)
        entry_start = start_point - direction * self.length
        entry_elevation = start_point.Z - self.length * entry_slope

        # Esquinas de entrada
        entry_inner = rg.Point3d(
            entry_start.X - lateral.X * entry_width / 2,
            entry_start.Y - lateral.Y * entry_width / 2,
            entry_elevation
        )
        entry_outer = rg.Point3d(
            entry_start.X + lateral.X * entry_width / 2,
            entry_start.Y + lateral.Y * entry_width / 2,
            entry_elevation
        )

        # Esquinas de la rampa
        ramp_inner = rg.Point3d(
            start_point.X - lateral.X * self.width / 2,
            start_point.Y - lateral.Y * self.width / 2,
            start_point.Z
        )
        ramp_outer = rg.Point3d(
            start_point.X + lateral.X * self.width / 2,
            start_point.Y + lateral.Y * self.width / 2,
            start_point.Z
        )

        # Crear superficie
        corners = [entry_inner, entry_outer, ramp_outer, ramp_inner]
        polyline = rg.Polyline(corners + [corners[0]])
        curve = polyline.ToNurbsCurve()

        surface = rg.Brep.CreatePlanarBreps(curve, 0.001)

        return surface[0] if surface else None

    def build_exit_transition(self, end_point, end_direction,
                               exit_width=None, exit_slope=0):
        """
        Construye transicion de salida.

        Similar a entrada pero en el otro extremo.
        """
        if exit_width is None:
            exit_width = self.width

        direction = rg.Vector3d(end_direction)
        direction.Unitize()

        lateral = rg.Vector3d.CrossProduct(direction, rg.Vector3d.ZAxis)
        lateral.Unitize()

        # Puntos de salida (despues de la rampa)
        exit_end = end_point + direction * self.length
        exit_elevation = end_point.Z + self.length * exit_slope

        # Esquinas
        ramp_inner = rg.Point3d(
            end_point.X - lateral.X * self.width / 2,
            end_point.Y - lateral.Y * self.width / 2,
            end_point.Z
        )
        ramp_outer = rg.Point3d(
            end_point.X + lateral.X * self.width / 2,
            end_point.Y + lateral.Y * self.width / 2,
            end_point.Z
        )

        exit_inner = rg.Point3d(
            exit_end.X - lateral.X * exit_width / 2,
            exit_end.Y - lateral.Y * exit_width / 2,
            exit_elevation
        )
        exit_outer = rg.Point3d(
            exit_end.X + lateral.X * exit_width / 2,
            exit_end.Y + lateral.Y * exit_width / 2,
            exit_elevation
        )

        corners = [ramp_inner, ramp_outer, exit_outer, exit_inner]
        polyline = rg.Polyline(corners + [corners[0]])
        curve = polyline.ToNurbsCurve()

        surface = rg.Brep.CreatePlanarBreps(curve, 0.001)

        return surface[0] if surface else None


class HelicalRampGenerator:
    """Generador principal de rampas helicoidales."""

    def __init__(self):
        pass

    def generate(self, inner_radius=7.5, outer_radius=12.5,
                 rise_per_turn=3.0, total_turns=2.0,
                 direction='clockwise', superelevation=4.0,
                 slab_thickness=0.25, center=None):
        """
        Genera rampa helicoidal completa.

        Args:
            inner_radius: Radio interior (m)
            outer_radius: Radio exterior (m)
            rise_per_turn: Altura por vuelta (m)
            total_turns: Numero de vueltas
            direction: Direccion de giro
            superelevation: Peralte maximo (%)
            slab_thickness: Espesor de losa (m)
            center: Punto central

        Returns:
            dict: Diccionario con geometrias
        """
        if center is None:
            center = rg.Point3d(0, 0, 0)

        # Crear generador de helice
        helix_gen = HelixCurveGenerator(
            inner_radius, outer_radius, rise_per_turn,
            total_turns, direction
        )

        # Calculador de peralte
        super_calc = SuperelevationCalculator(superelevation)

        # Constructor de superficie
        surface_builder = RampSurfaceBuilder(helix_gen, super_calc)

        # Generar secciones
        sections = surface_builder.generate_sections(section_count=100)

        # Construir solido de losa
        slab = surface_builder.build_slab_solid(sections, slab_thickness)

        # Obtener geometria de helice
        helix_geometry = helix_gen.get_geometry()

        # Mover al centro si es necesario
        if center.X != 0 or center.Y != 0 or center.Z != 0:
            transform = rg.Transform.Translation(rg.Vector3d(center))
            if slab:
                slab.Transform(transform)
            if helix_geometry.surface:
                helix_geometry.surface.Transform(transform)

        return {
            'slab': slab,
            'surface': helix_geometry.surface,
            'inner_helix': helix_geometry.inner_helix,
            'outer_helix': helix_geometry.outer_helix,
            'centerline': helix_geometry.centerline,
            'sections': sections,
            'statistics': {
                'total_rise': helix_geometry.total_rise,
                'total_length': helix_geometry.total_length,
                'slope_percent': helix_geometry.slope,
                'inner_radius': inner_radius,
                'outer_radius': outer_radius,
                'width': outer_radius - inner_radius,
                'turns': total_turns
            }
        }


# Funciones de utilidad para Grasshopper
def create_ramp_curves(inner_radius, outer_radius, rise_per_turn,
                       total_turns, direction='clockwise'):
    """
    Crea curvas de la rampa para visualizacion.

    Returns:
        tuple: (inner_curve, outer_curve, centerline)
    """
    helix_gen = HelixCurveGenerator(
        inner_radius, outer_radius, rise_per_turn, total_turns, direction
    )

    return (
        helix_gen.generate_inner_helix(),
        helix_gen.generate_outer_helix(),
        helix_gen.generate_centerline()
    )


def calculate_ramp_statistics(inner_radius, outer_radius, rise_per_turn,
                               total_turns):
    """
    Calcula estadisticas de la rampa.

    Returns:
        dict: Estadisticas
    """
    center_radius = (inner_radius + outer_radius) / 2.0
    center_length = 2 * math.pi * center_radius * total_turns
    total_rise = rise_per_turn * total_turns
    slope = (total_rise / center_length) * 100
    width = outer_radius - inner_radius
    area = math.pi * (outer_radius ** 2 - inner_radius ** 2) * total_turns

    return {
        'center_length': center_length,
        'total_rise': total_rise,
        'slope_percent': slope,
        'width': width,
        'area': area,
        'inner_length': 2 * math.pi * inner_radius * total_turns,
        'outer_length': 2 * math.pi * outer_radius * total_turns
    }


# Ejemplo de uso
if __name__ == "__main__":
    generator = HelicalRampGenerator()

    result = generator.generate(
        inner_radius=7.5,
        outer_radius=12.5,
        rise_per_turn=3.0,
        total_turns=2.0,
        direction='clockwise',
        superelevation=4.0,
        slab_thickness=0.25
    )

    stats = result['statistics']
    print(f"Longitud total: {stats['total_length']:.1f} m")
    print(f"Altura total: {stats['total_rise']:.1f} m")
    print(f"Pendiente: {stats['slope_percent']:.1f}%")
    print(f"Ancho: {stats['width']:.1f} m")
