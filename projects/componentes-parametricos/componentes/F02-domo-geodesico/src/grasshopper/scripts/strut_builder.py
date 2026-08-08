#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Barras - F02 Domo Geodesico Parametrico

Genera la geometria de barras estructurales (struts) del domo
con perfiles tubulares y preparacion para nodos.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
StrutGeometry = namedtuple('StrutGeometry', [
    'index', 'brep', 'axis', 'length', 'chord_type',
    'start_node', 'end_node', 'profile'
])

ProfileData = namedtuple('ProfileData', [
    'name', 'type', 'diameter', 'wall', 'area', 'I', 'weight'
])


class TubularProfileDatabase:
    """Base de datos de perfiles tubulares."""

    PROFILES = {
        # Tubos circulares
        'D33x2': ProfileData('D33x2', 'round', 33.4, 2.0, 197, 22600, 1.56),
        'D42x2.5': ProfileData('D42x2.5', 'round', 42.2, 2.5, 312, 56200, 2.45),
        'D48x3': ProfileData('D48x3', 'round', 48.3, 3.0, 427, 94500, 3.35),
        'D60x3': ProfileData('D60x3', 'round', 60.3, 3.0, 540, 189000, 4.24),
        'D76x4': ProfileData('D76x4', 'round', 76.1, 4.0, 906, 493000, 7.11),
        'D89x4': ProfileData('D89x4', 'round', 88.9, 4.0, 1068, 802000, 8.38),
        'D114x5': ProfileData('D114x5', 'round', 114.3, 5.0, 1717, 2120000, 13.5),
        'D140x6': ProfileData('D140x6', 'round', 139.7, 6.0, 2521, 4640000, 19.8),
        'D168x6': ProfileData('D168x6', 'round', 168.3, 6.0, 3058, 8170000, 24.0),
    }

    @classmethod
    def get_profile(cls, name):
        """Obtiene datos del perfil."""
        return cls.PROFILES.get(name, cls.PROFILES['D60x3'])

    @classmethod
    def get_outer_radius(cls, name):
        """Obtiene radio exterior en metros."""
        profile = cls.get_profile(name)
        return profile.diameter / 2000.0  # mm a m

    @classmethod
    def get_inner_radius(cls, name):
        """Obtiene radio interior en metros."""
        profile = cls.get_profile(name)
        return (profile.diameter - 2 * profile.wall) / 2000.0

    @classmethod
    def select_profile_for_span(cls, span, load_factor=1.0):
        """
        Selecciona perfil adecuado para el claro.

        Args:
            span: Longitud de la barra en m
            load_factor: Factor de carga

        Returns:
            str: Nombre del perfil
        """
        # Criterio simplificado: L/r < 200 para compresion
        # r = sqrt(I/A)

        for name, profile in sorted(cls.PROFILES.items(),
                                     key=lambda x: x[1].diameter):
            r = math.sqrt(profile.I / profile.area) / 1000.0  # mm a m
            slenderness = span / r

            if slenderness < 200 / load_factor:
                return name

        return 'D168x6'  # El mas grande si ninguno cumple


class StrutEndProcessor:
    """Procesa extremos de barras para conexion a nodos."""

    def __init__(self, node_radius):
        """
        Args:
            node_radius: Radio del nodo en metros
        """
        self.node_radius = node_radius

    def calculate_trim_distance(self, strut_angle_to_node):
        """
        Calcula distancia de recorte del extremo.

        Args:
            strut_angle_to_node: Angulo de la barra respecto al nodo

        Returns:
            float: Distancia de recorte
        """
        # Para nodos esfericos, el recorte depende del angulo
        return self.node_radius / math.cos(strut_angle_to_node / 2.0)

    def create_flat_end(self, axis_line, end_point, profile_radius):
        """
        Crea extremo plano perpendicular al eje.

        Args:
            axis_line: Linea del eje de la barra
            end_point: Punto del extremo
            profile_radius: Radio del perfil

        Returns:
            Brep: Superficie plana del extremo
        """
        direction = rg.Vector3d(axis_line.Direction)
        direction.Unitize()

        plane = rg.Plane(end_point, direction)
        circle = rg.Circle(plane, profile_radius)

        return rg.Brep.CreatePlanarBreps(circle.ToNurbsCurve(), 0.001)[0]

    def create_spherical_cut_end(self, axis_line, end_point, profile_radius,
                                  node_center, node_radius):
        """
        Crea extremo cortado esfericamente para ajuste a nodo.

        Args:
            axis_line: Linea del eje
            end_point: Punto del extremo
            profile_radius: Radio del perfil
            node_center: Centro del nodo
            node_radius: Radio del nodo

        Returns:
            Brep: Superficie del extremo cortado
        """
        # Crear esfera del nodo
        sphere = rg.Sphere(node_center, node_radius)

        # Crear tubo del strut
        direction = rg.Vector3d(axis_line.Direction)
        direction.Unitize()

        # El corte es la interseccion del cilindro con la esfera
        # Por simplicidad, retornamos un plano inclinado
        to_center = rg.Vector3d(node_center - end_point)
        to_center.Unitize()

        plane = rg.Plane(end_point, to_center)
        circle = rg.Circle(plane, profile_radius)

        breps = rg.Brep.CreatePlanarBreps(circle.ToNurbsCurve(), 0.001)
        return breps[0] if breps else None


class CircularStrutBuilder:
    """Construye barras con perfil tubular circular."""

    def __init__(self, profile_name='D60x3'):
        """
        Args:
            profile_name: Nombre del perfil de la base de datos
        """
        self.profile_name = profile_name
        self.profile = TubularProfileDatabase.get_profile(profile_name)
        self.outer_radius = TubularProfileDatabase.get_outer_radius(profile_name)
        self.inner_radius = TubularProfileDatabase.get_inner_radius(profile_name)

    def build_strut(self, start_point, end_point, hollow=True):
        """
        Construye una barra tubular.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            hollow: Si es hueco (tubo) o solido

        Returns:
            Brep: Geometria de la barra
        """
        # Eje de la barra
        axis = rg.Line(start_point, end_point)

        # Plano en el inicio
        direction = rg.Vector3d(end_point - start_point)
        direction.Unitize()
        plane = rg.Plane(start_point, direction)

        # Circulo exterior
        outer_circle = rg.Circle(plane, self.outer_radius)

        if hollow and self.inner_radius > 0:
            # Circulo interior
            inner_circle = rg.Circle(plane, self.inner_radius)

            # Crear anillo
            outer_curve = outer_circle.ToNurbsCurve()
            inner_curve = inner_circle.ToNurbsCurve()

            # Extruir ambos y hacer diferencia
            extrusion_vec = rg.Vector3d(end_point - start_point)

            outer_brep = rg.Brep.CreateFromCylinder(
                rg.Cylinder(outer_circle, axis.Length), True, True
            )
            inner_brep = rg.Brep.CreateFromCylinder(
                rg.Cylinder(inner_circle, axis.Length), True, True
            )

            if outer_brep and inner_brep:
                result = rg.Brep.CreateBooleanDifference(
                    outer_brep, inner_brep, 0.001
                )
                if result and len(result) > 0:
                    return result[0]

            return outer_brep

        else:
            # Cilindro solido
            cylinder = rg.Cylinder(outer_circle, axis.Length)
            return rg.Brep.CreateFromCylinder(cylinder, True, True)

    def build_strut_simplified(self, start_point, end_point):
        """
        Construye barra simplificada (cilindro solido).

        Args:
            start_point: Punto inicial
            end_point: Punto final

        Returns:
            Brep: Cilindro solido
        """
        axis = rg.Line(start_point, end_point)

        direction = rg.Vector3d(end_point - start_point)
        direction.Unitize()
        plane = rg.Plane(start_point, direction)

        circle = rg.Circle(plane, self.outer_radius)
        cylinder = rg.Cylinder(circle, axis.Length)

        return rg.Brep.CreateFromCylinder(cylinder, True, True)


class StrutAssemblyBuilder:
    """Construye el ensamble completo de barras del domo."""

    def __init__(self, geodesic_mesh, profile_name='D60x3',
                 node_radius=0.05, simplified=True):
        """
        Args:
            geodesic_mesh: GeodesicMesh del generador
            profile_name: Perfil a usar
            node_radius: Radio de los nodos
            simplified: Usar geometria simplificada
        """
        self.mesh = geodesic_mesh
        self.profile_name = profile_name
        self.node_radius = node_radius
        self.simplified = simplified
        self.strut_builder = CircularStrutBuilder(profile_name)

    def build_all_struts(self):
        """
        Construye todas las barras del domo.

        Returns:
            list: Lista de StrutGeometry
        """
        struts = []

        for edge in self.mesh.edges:
            # Obtener puntos
            start_vertex = self.mesh.vertices[edge.start]
            end_vertex = self.mesh.vertices[edge.end]

            start_point = start_vertex.point
            end_point = end_vertex.point

            # Acortar por nodos
            direction = rg.Vector3d(end_point - start_point)
            direction.Unitize()

            trimmed_start = rg.Point3d(
                start_point.X + direction.X * self.node_radius,
                start_point.Y + direction.Y * self.node_radius,
                start_point.Z + direction.Z * self.node_radius
            )

            trimmed_end = rg.Point3d(
                end_point.X - direction.X * self.node_radius,
                end_point.Y - direction.Y * self.node_radius,
                end_point.Z - direction.Z * self.node_radius
            )

            # Construir barra
            if self.simplified:
                brep = self.strut_builder.build_strut_simplified(
                    trimmed_start, trimmed_end
                )
            else:
                brep = self.strut_builder.build_strut(
                    trimmed_start, trimmed_end, hollow=True
                )

            # Crear eje
            axis = rg.Line(start_point, end_point)

            struts.append(StrutGeometry(
                index=edge.index,
                brep=brep,
                axis=axis,
                length=edge.length,
                chord_type=edge.chord_type,
                start_node=edge.start,
                end_node=edge.end,
                profile=self.profile_name
            ))

        return struts

    def build_struts_by_type(self):
        """
        Construye barras agrupadas por tipo.

        Returns:
            dict: {chord_type: [StrutGeometry]}
        """
        struts = self.build_all_struts()

        grouped = {}
        for strut in struts:
            t = strut.chord_type
            if t not in grouped:
                grouped[t] = []
            grouped[t].append(strut)

        return grouped

    def get_cut_list(self):
        """
        Genera lista de corte para fabricacion.

        Returns:
            list: Lista de dicts con informacion de corte
        """
        struts = self.build_all_struts()

        # Agrupar por tipo y contar
        type_counts = {}
        for strut in struts:
            t = strut.chord_type
            if t not in type_counts:
                type_counts[t] = {
                    'count': 0,
                    'length': strut.length,
                    'effective_length': strut.length - 2 * self.node_radius
                }
            type_counts[t]['count'] += 1

        # Crear lista de corte
        cut_list = []
        for chord_type, data in sorted(type_counts.items()):
            cut_list.append({
                'type': chord_type,
                'profile': self.profile_name,
                'quantity': data['count'],
                'cut_length_mm': data['effective_length'] * 1000,
                'total_length_m': data['count'] * data['effective_length'],
                'weight_kg': data['count'] * data['effective_length'] * \
                    self.strut_builder.profile.weight
            })

        return cut_list


class StrutAnalyzer:
    """Analiza propiedades estructurales de las barras."""

    def __init__(self, struts, profile_name):
        """
        Args:
            struts: Lista de StrutGeometry
            profile_name: Nombre del perfil
        """
        self.struts = struts
        self.profile = TubularProfileDatabase.get_profile(profile_name)

    def calculate_total_weight(self):
        """Calcula peso total de barras en kg."""
        total_length = sum(s.length for s in self.struts)
        return total_length * self.profile.weight

    def calculate_slenderness(self):
        """
        Calcula esbeltez de cada barra.

        Returns:
            dict: {chord_type: slenderness}
        """
        r = math.sqrt(self.profile.I / self.profile.area) / 1000.0  # m

        slenderness = {}
        for strut in self.struts:
            if strut.chord_type not in slenderness:
                slenderness[strut.chord_type] = strut.length / r

        return slenderness

    def check_capacity(self, axial_load, Fy=250):
        """
        Verifica capacidad de las barras.

        Args:
            axial_load: Carga axial en kN
            Fy: Esfuerzo de fluencia en MPa

        Returns:
            dict: Resultados de verificacion
        """
        slenderness = self.calculate_slenderness()

        results = {}
        for chord_type, kl_r in slenderness.items():
            # Esfuerzo critico de Euler
            E = 200000  # MPa
            Fe = math.pi ** 2 * E / (kl_r ** 2)

            # Esfuerzo critico segun AISC
            if kl_r <= 4.71 * math.sqrt(E / Fy):
                Fcr = 0.658 ** (Fy / Fe) * Fy
            else:
                Fcr = 0.877 * Fe

            # Capacidad
            phi = 0.9
            Pn = phi * Fcr * self.profile.area / 1000  # kN

            results[chord_type] = {
                'slenderness': kl_r,
                'Fe': Fe,
                'Fcr': Fcr,
                'capacity_kN': Pn,
                'demand_kN': axial_load,
                'ratio': axial_load / Pn if Pn > 0 else float('inf'),
                'status': 'OK' if axial_load < Pn else 'NG'
            }

        return results


# Funciones de utilidad para Grasshopper
def create_strut_lines(geodesic_mesh):
    """
    Crea lineas de las barras para visualizacion.

    Args:
        geodesic_mesh: GeodesicMesh

    Returns:
        list: Lista de Line
    """
    lines = []
    for edge in geodesic_mesh.edges:
        start = geodesic_mesh.vertices[edge.start].point
        end = geodesic_mesh.vertices[edge.end].point
        lines.append(rg.Line(start, end))
    return lines


def create_strut_curves(geodesic_mesh, node_radius=0.05):
    """
    Crea curvas de las barras recortadas por nodos.

    Args:
        geodesic_mesh: GeodesicMesh
        node_radius: Radio del nodo

    Returns:
        list: Lista de LineCurve
    """
    curves = []
    for edge in geodesic_mesh.edges:
        start = geodesic_mesh.vertices[edge.start].point
        end = geodesic_mesh.vertices[edge.end].point

        direction = rg.Vector3d(end - start)
        direction.Unitize()

        trimmed_start = start + direction * node_radius
        trimmed_end = end - direction * node_radius

        curves.append(rg.LineCurve(trimmed_start, trimmed_end))

    return curves


# Ejemplo de uso
if __name__ == "__main__":
    from geodesic_generator import GeodesicDomeGenerator

    # Generar domo
    generator = GeodesicDomeGenerator()
    mesh = generator.generate(radius=10.0, frequency=3, truncation=0.5)

    # Construir barras
    strut_builder = StrutAssemblyBuilder(mesh, profile_name='D60x3')
    struts = strut_builder.build_all_struts()

    # Lista de corte
    cut_list = strut_builder.get_cut_list()
    for item in cut_list:
        print(f"Tipo {item['type']}: {item['quantity']} piezas x "
              f"{item['cut_length_mm']:.0f}mm = {item['weight_kg']:.1f}kg")

    # Peso total
    analyzer = StrutAnalyzer(struts, 'D60x3')
    print(f"\nPeso total: {analyzer.calculate_total_weight():.1f} kg")
