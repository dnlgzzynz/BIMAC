#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de Geometria Geodesica - F02 Domo Geodesico Parametrico

Genera la geometria base de domos geodesicos mediante subdivision
de poliedros regulares (icosaedro, octaedro, tetraedro).

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
Vertex = namedtuple('Vertex', ['index', 'point', 'type'])
Edge = namedtuple('Edge', ['index', 'start', 'end', 'length', 'chord_type'])
Face = namedtuple('Face', ['index', 'vertices', 'centroid', 'normal', 'area'])
GeodesicMesh = namedtuple('GeodesicMesh', ['vertices', 'edges', 'faces', 'radius', 'frequency'])


class IcosahedronGenerator:
    """Genera icosaedro base para subdivision geodesica."""

    # Proporcion aurea
    PHI = (1.0 + math.sqrt(5.0)) / 2.0

    def __init__(self, radius=1.0):
        """
        Inicializa generador de icosaedro.

        Args:
            radius: Radio de la esfera circunscrita
        """
        self.radius = radius

    def generate_vertices(self):
        """
        Genera los 12 vertices del icosaedro.

        Returns:
            list: Lista de Point3d
        """
        # Vertices en coordenadas normalizadas
        # Basado en rectangulos dorados ortogonales
        phi = self.PHI
        scale = self.radius / math.sqrt(1 + phi * phi)

        vertices = [
            rg.Point3d(0, 1, phi),
            rg.Point3d(0, -1, phi),
            rg.Point3d(0, 1, -phi),
            rg.Point3d(0, -1, -phi),
            rg.Point3d(1, phi, 0),
            rg.Point3d(-1, phi, 0),
            rg.Point3d(1, -phi, 0),
            rg.Point3d(-1, -phi, 0),
            rg.Point3d(phi, 0, 1),
            rg.Point3d(-phi, 0, 1),
            rg.Point3d(phi, 0, -1),
            rg.Point3d(-phi, 0, -1)
        ]

        # Escalar y proyectar a esfera
        result = []
        for v in vertices:
            vec = rg.Vector3d(v)
            vec.Unitize()
            vec *= self.radius
            result.append(rg.Point3d(vec.X, vec.Y, vec.Z))

        return result

    def generate_faces(self):
        """
        Genera las 20 caras triangulares del icosaedro.

        Returns:
            list: Lista de tuplas (v1, v2, v3) indices de vertices
        """
        # Indices de vertices para cada cara (ordenados CCW visto desde afuera)
        faces = [
            (0, 1, 8), (0, 8, 4), (0, 4, 5), (0, 5, 9), (0, 9, 1),
            (1, 6, 8), (8, 6, 10), (8, 10, 4), (4, 10, 2), (4, 2, 5),
            (5, 2, 11), (5, 11, 9), (9, 11, 7), (9, 7, 1), (1, 7, 6),
            (3, 6, 7), (3, 7, 11), (3, 11, 2), (3, 2, 10), (3, 10, 6)
        ]
        return faces

    def generate(self):
        """
        Genera icosaedro completo.

        Returns:
            tuple: (vertices, faces)
        """
        return self.generate_vertices(), self.generate_faces()


class OctahedronGenerator:
    """Genera octaedro base para subdivision geodesica."""

    def __init__(self, radius=1.0):
        self.radius = radius

    def generate_vertices(self):
        """Genera los 6 vertices del octaedro."""
        r = self.radius
        vertices = [
            rg.Point3d(r, 0, 0),
            rg.Point3d(-r, 0, 0),
            rg.Point3d(0, r, 0),
            rg.Point3d(0, -r, 0),
            rg.Point3d(0, 0, r),
            rg.Point3d(0, 0, -r)
        ]
        return vertices

    def generate_faces(self):
        """Genera las 8 caras del octaedro."""
        faces = [
            (4, 0, 2), (4, 2, 1), (4, 1, 3), (4, 3, 0),
            (5, 2, 0), (5, 1, 2), (5, 3, 1), (5, 0, 3)
        ]
        return faces

    def generate(self):
        return self.generate_vertices(), self.generate_faces()


class TetrahedronGenerator:
    """Genera tetraedro base para subdivision geodesica."""

    def __init__(self, radius=1.0):
        self.radius = radius

    def generate_vertices(self):
        """Genera los 4 vertices del tetraedro."""
        r = self.radius
        # Tetraedro inscrito en esfera
        a = r / math.sqrt(3)
        h = r * math.sqrt(2.0 / 3.0)

        vertices = [
            rg.Point3d(0, 0, r),
            rg.Point3d(2 * a, 0, -r / 3),
            rg.Point3d(-a, a * math.sqrt(3), -r / 3),
            rg.Point3d(-a, -a * math.sqrt(3), -r / 3)
        ]

        # Proyectar a esfera
        result = []
        for v in vertices:
            vec = rg.Vector3d(v)
            vec.Unitize()
            vec *= r
            result.append(rg.Point3d(vec.X, vec.Y, vec.Z))

        return result

    def generate_faces(self):
        """Genera las 4 caras del tetraedro."""
        faces = [
            (0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)
        ]
        return faces

    def generate(self):
        return self.generate_vertices(), self.generate_faces()


class GeodesicSubdivider:
    """Subdivide poliedros para crear geometria geodesica."""

    def __init__(self, radius=1.0):
        self.radius = radius
        self.vertex_cache = {}

    def _get_midpoint(self, p1, p2, vertex_list):
        """
        Obtiene punto medio proyectado a la esfera.

        Args:
            p1, p2: Indices de vertices
            vertex_list: Lista de vertices actuales

        Returns:
            int: Indice del nuevo vertice
        """
        # Crear clave unica para el edge
        key = tuple(sorted([p1, p2]))

        if key in self.vertex_cache:
            return self.vertex_cache[key]

        # Calcular punto medio
        v1 = vertex_list[p1]
        v2 = vertex_list[p2]

        mid = rg.Point3d(
            (v1.X + v2.X) / 2.0,
            (v1.Y + v2.Y) / 2.0,
            (v1.Z + v2.Z) / 2.0
        )

        # Proyectar a esfera
        vec = rg.Vector3d(mid)
        vec.Unitize()
        vec *= self.radius
        projected = rg.Point3d(vec.X, vec.Y, vec.Z)

        # Agregar a lista
        new_index = len(vertex_list)
        vertex_list.append(projected)
        self.vertex_cache[key] = new_index

        return new_index

    def subdivide(self, vertices, faces, frequency):
        """
        Subdivide la malla al nivel de frecuencia especificado.

        Args:
            vertices: Lista de vertices iniciales
            faces: Lista de caras (tuplas de indices)
            frequency: Nivel de subdivision (1-8)

        Returns:
            tuple: (vertices, faces) subdivididos
        """
        current_vertices = list(vertices)
        current_faces = list(faces)

        for _ in range(frequency - 1):
            self.vertex_cache = {}
            new_faces = []

            for face in current_faces:
                v1, v2, v3 = face

                # Obtener puntos medios
                a = self._get_midpoint(v1, v2, current_vertices)
                b = self._get_midpoint(v2, v3, current_vertices)
                c = self._get_midpoint(v3, v1, current_vertices)

                # Crear 4 nuevas caras
                new_faces.append((v1, a, c))
                new_faces.append((v2, b, a))
                new_faces.append((v3, c, b))
                new_faces.append((a, b, c))

            current_faces = new_faces

        return current_vertices, current_faces


class DomeTruncator:
    """Trunca esfera geodesica para crear domos."""

    def __init__(self, truncation_ratio=0.5):
        """
        Args:
            truncation_ratio: 0.25 = 1/4, 0.5 = hemisferio, 1.0 = esfera completa
        """
        self.truncation_ratio = truncation_ratio

    def get_cut_height(self, radius):
        """
        Calcula altura de corte.

        Args:
            radius: Radio de la esfera

        Returns:
            float: Altura Z de corte (vertices debajo se eliminan)
        """
        # Truncation ratio de 0.5 = hemisferio (corte en Z=0)
        # Truncation ratio de 1.0 = esfera completa (corte en Z=-radius)
        # Truncation ratio de 0.25 = 1/4 esfera (corte en Z=radius/2)
        return radius * (1.0 - 2.0 * self.truncation_ratio)

    def truncate(self, vertices, faces, radius):
        """
        Trunca la malla geodesica.

        Args:
            vertices: Lista de vertices
            faces: Lista de caras
            radius: Radio de la esfera

        Returns:
            tuple: (vertices, faces, base_vertices) truncados
        """
        cut_height = self.get_cut_height(radius)

        # Identificar vertices validos
        valid_vertices = set()
        for i, v in enumerate(vertices):
            if v.Z >= cut_height - 0.001:  # Tolerancia
                valid_vertices.add(i)

        # Crear mapeo de indices
        new_indices = {}
        new_vertices = []
        base_vertices = []  # Vertices cerca del corte

        for i, v in enumerate(vertices):
            if i in valid_vertices:
                new_indices[i] = len(new_vertices)
                new_vertices.append(v)

                # Verificar si esta cerca del corte
                if abs(v.Z - cut_height) < radius * 0.1:
                    base_vertices.append(new_indices[i])

        # Filtrar caras
        new_faces = []
        for face in faces:
            if all(v in valid_vertices for v in face):
                new_face = tuple(new_indices[v] for v in face)
                new_faces.append(new_face)

        return new_vertices, new_faces, base_vertices


class EdgeAnalyzer:
    """Analiza y clasifica bordes de la malla geodesica."""

    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces

    def extract_edges(self):
        """
        Extrae todos los bordes unicos de las caras.

        Returns:
            list: Lista de Edge namedtuples
        """
        edge_set = set()
        edge_lengths = {}

        for face in self.faces:
            for i in range(3):
                v1 = face[i]
                v2 = face[(i + 1) % 3]

                # Ordenar para evitar duplicados
                edge = tuple(sorted([v1, v2]))
                edge_set.add(edge)

                # Calcular longitud
                if edge not in edge_lengths:
                    p1 = self.vertices[v1]
                    p2 = self.vertices[v2]
                    length = p1.DistanceTo(p2)
                    edge_lengths[edge] = length

        # Clasificar bordes por longitud
        lengths = list(set(edge_lengths.values()))
        lengths.sort()

        # Crear tolerancia para agrupar
        tolerance = lengths[0] * 0.01 if lengths else 0.001
        chord_types = {}

        for length in lengths:
            found = False
            for existing_type, ref_length in chord_types.items():
                if abs(length - ref_length) < tolerance:
                    found = True
                    break
            if not found:
                chord_types[chr(ord('A') + len(chord_types))] = length

        # Crear lista de Edge
        edges = []
        for i, (v1, v2) in enumerate(edge_set):
            length = edge_lengths[(v1, v2)]

            # Encontrar tipo
            edge_type = 'A'
            for t, ref_length in chord_types.items():
                if abs(length - ref_length) < tolerance:
                    edge_type = t
                    break

            edges.append(Edge(
                index=i,
                start=v1,
                end=v2,
                length=length,
                chord_type=edge_type
            ))

        return edges


class FaceAnalyzer:
    """Analiza caras de la malla geodesica."""

    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces

    def analyze_faces(self):
        """
        Analiza todas las caras.

        Returns:
            list: Lista de Face namedtuples
        """
        analyzed = []

        for i, face in enumerate(self.faces):
            v1, v2, v3 = face
            p1 = self.vertices[v1]
            p2 = self.vertices[v2]
            p3 = self.vertices[v3]

            # Centroide
            centroid = rg.Point3d(
                (p1.X + p2.X + p3.X) / 3.0,
                (p1.Y + p2.Y + p3.Y) / 3.0,
                (p1.Z + p2.Z + p3.Z) / 3.0
            )

            # Normal
            vec1 = rg.Vector3d(p2 - p1)
            vec2 = rg.Vector3d(p3 - p1)
            normal = rg.Vector3d.CrossProduct(vec1, vec2)
            normal.Unitize()

            # Area (formula de Heron)
            a = p1.DistanceTo(p2)
            b = p2.DistanceTo(p3)
            c = p3.DistanceTo(p1)
            s = (a + b + c) / 2.0
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))

            analyzed.append(Face(
                index=i,
                vertices=face,
                centroid=centroid,
                normal=normal,
                area=area
            ))

        return analyzed


class GeodesicDomeGenerator:
    """Generador principal de domos geodesicos."""

    def __init__(self):
        self.polyhedron_generators = {
            'icosahedron': IcosahedronGenerator,
            'octahedron': OctahedronGenerator,
            'tetrahedron': TetrahedronGenerator
        }

    def generate(self, radius=10.0, frequency=3, truncation=0.5,
                 base_type='icosahedron', center=None):
        """
        Genera un domo geodesico completo.

        Args:
            radius: Radio del domo en unidades del modelo
            frequency: Frecuencia de subdivision (1-8)
            truncation: Ratio de truncamiento (0.25-1.0)
            base_type: Tipo de poliedro base
            center: Punto central del domo (default: origen)

        Returns:
            GeodesicMesh: Malla geodesica con vertices, edges, faces
        """
        if center is None:
            center = rg.Point3d(0, 0, 0)

        # Validar parametros
        frequency = max(1, min(8, int(frequency)))
        truncation = max(0.1, min(1.0, truncation))

        # Generar poliedro base
        generator_class = self.polyhedron_generators.get(
            base_type, IcosahedronGenerator
        )
        base_generator = generator_class(radius)
        vertices, faces = base_generator.generate()

        # Subdividir
        subdivider = GeodesicSubdivider(radius)
        vertices, faces = subdivider.subdivide(vertices, faces, frequency)

        # Truncar
        truncator = DomeTruncator(truncation)
        vertices, faces, base_verts = truncator.truncate(vertices, faces, radius)

        # Mover al centro
        if center.X != 0 or center.Y != 0 or center.Z != 0:
            move_vec = rg.Vector3d(center)
            vertices = [
                rg.Point3d(v.X + center.X, v.Y + center.Y, v.Z + center.Z)
                for v in vertices
            ]

        # Analizar edges
        edge_analyzer = EdgeAnalyzer(vertices, faces)
        edges = edge_analyzer.extract_edges()

        # Analizar faces
        face_analyzer = FaceAnalyzer(vertices, faces)
        analyzed_faces = face_analyzer.analyze_faces()

        # Crear vertices tipados
        typed_vertices = []
        base_set = set(base_verts)
        for i, v in enumerate(vertices):
            v_type = 'base' if i in base_set else 'dome'
            typed_vertices.append(Vertex(
                index=i,
                point=v,
                type=v_type
            ))

        return GeodesicMesh(
            vertices=typed_vertices,
            edges=edges,
            faces=analyzed_faces,
            radius=radius,
            frequency=frequency
        )

    def get_statistics(self, mesh):
        """
        Obtiene estadisticas del domo.

        Args:
            mesh: GeodesicMesh

        Returns:
            dict: Estadisticas
        """
        # Contar tipos de bordes
        edge_types = {}
        for edge in mesh.edges:
            t = edge.chord_type
            if t not in edge_types:
                edge_types[t] = {'count': 0, 'length': edge.length}
            edge_types[t]['count'] += 1

        # Calcular areas
        total_area = sum(f.area for f in mesh.faces)

        # Longitudes de barras
        total_strut_length = sum(e.length for e in mesh.edges)

        return {
            'vertex_count': len(mesh.vertices),
            'edge_count': len(mesh.edges),
            'face_count': len(mesh.faces),
            'edge_types': edge_types,
            'unique_strut_lengths': len(edge_types),
            'total_surface_area': total_area,
            'total_strut_length': total_strut_length,
            'radius': mesh.radius,
            'frequency': mesh.frequency
        }


class BaseRingGenerator:
    """Genera anillo base para apoyo del domo."""

    def __init__(self, mesh, floor_level=0.0):
        """
        Args:
            mesh: GeodesicMesh del domo
            floor_level: Nivel Z del piso
        """
        self.mesh = mesh
        self.floor_level = floor_level

    def get_base_vertices(self):
        """Obtiene vertices de la base ordenados circularmente."""
        base_verts = [v for v in self.mesh.vertices if v.type == 'base']

        # Ordenar por angulo
        center = rg.Point3d(0, 0, 0)
        base_verts.sort(key=lambda v: math.atan2(
            v.point.Y - center.Y,
            v.point.X - center.X
        ))

        return base_verts

    def generate_ring_polygon(self):
        """
        Genera poligono del anillo base.

        Returns:
            Polyline: Polilinea cerrada del anillo
        """
        base_verts = self.get_base_vertices()

        # Proyectar a nivel de piso
        points = [
            rg.Point3d(v.point.X, v.point.Y, self.floor_level)
            for v in base_verts
        ]

        # Cerrar polilinea
        if points:
            points.append(points[0])

        return rg.Polyline(points)

    def generate_ring_beam(self, profile_radius=0.05):
        """
        Genera viga de anillo como Brep.

        Args:
            profile_radius: Radio del perfil tubular

        Returns:
            Brep: Geometria del anillo
        """
        polyline = self.generate_ring_polygon()

        if polyline.Count < 3:
            return None

        curve = polyline.ToNurbsCurve()
        circle = rg.Circle(curve.PointAtStart, profile_radius)
        profile = circle.ToNurbsCurve()

        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(curve, profile)

        if breps and len(breps) > 0:
            return breps[0]

        return None


# Ejemplo de uso
if __name__ == "__main__":
    # Crear generador
    generator = GeodesicDomeGenerator()

    # Generar domo
    dome = generator.generate(
        radius=10.0,
        frequency=3,
        truncation=0.5,
        base_type='icosahedron'
    )

    # Obtener estadisticas
    stats = generator.get_statistics(dome)
    print(f"Vertices: {stats['vertex_count']}")
    print(f"Edges: {stats['edge_count']}")
    print(f"Faces: {stats['face_count']}")
    print(f"Unique strut lengths: {stats['unique_strut_lengths']}")
    print(f"Total area: {stats['total_surface_area']:.2f} m2")
