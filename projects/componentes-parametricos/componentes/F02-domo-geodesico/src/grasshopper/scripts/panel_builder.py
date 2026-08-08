#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Paneles - F02 Domo Geodesico Parametrico

Genera la geometria de paneles de cerramiento para domos geodesicos
incluyendo paneles triangulares, hexagonales y sistemas mixtos.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
PanelGeometry = namedtuple('PanelGeometry', [
    'index', 'brep', 'frame', 'glazing', 'area',
    'panel_type', 'vertices', 'normal'
])

FrameMember = namedtuple('FrameMember', [
    'curve', 'profile', 'length'
])

PanelMaterial = namedtuple('PanelMaterial', [
    'name', 'thickness', 'density', 'u_value', 'cost_per_m2'
])


class PanelMaterialDatabase:
    """Base de datos de materiales para paneles."""

    MATERIALS = {
        'glass_single': PanelMaterial(
            'Vidrio simple templado', 8, 2500, 5.7, 180
        ),
        'glass_double': PanelMaterial(
            'Vidrio doble', 24, 2500, 2.8, 320
        ),
        'polycarbonate': PanelMaterial(
            'Policarbonato multicelular', 16, 1200, 2.3, 85
        ),
        'etfe': PanelMaterial(
            'ETFE cushion', 0.25, 350, 3.5, 250
        ),
        'aluminum': PanelMaterial(
            'Aluminio composite', 4, 2700, 6.0, 95
        ),
        'steel': PanelMaterial(
            'Acero galvanizado', 1.2, 7850, 6.5, 65
        )
    }

    @classmethod
    def get_material(cls, name):
        """Obtiene datos del material."""
        return cls.MATERIALS.get(name, cls.MATERIALS['glass_single'])


class TriangularPanelBuilder:
    """Construye paneles triangulares."""

    def __init__(self, frame_width=0.050, frame_depth=0.080,
                 glazing_offset=0.015, material='glass_single'):
        """
        Args:
            frame_width: Ancho del marco
            frame_depth: Profundidad del marco
            glazing_offset: Offset del vidrio desde el borde
            material: Material del panel
        """
        self.frame_width = frame_width
        self.frame_depth = frame_depth
        self.glazing_offset = glazing_offset
        self.material = PanelMaterialDatabase.get_material(material)

    def build_panel(self, vertices, face_index=0):
        """
        Construye un panel triangular completo.

        Args:
            vertices: Lista de 3 Point3d
            face_index: Indice de la cara

        Returns:
            PanelGeometry
        """
        if len(vertices) != 3:
            return None

        p1, p2, p3 = vertices

        # Calcular normal
        vec1 = rg.Vector3d(p2 - p1)
        vec2 = rg.Vector3d(p3 - p1)
        normal = rg.Vector3d.CrossProduct(vec1, vec2)
        normal.Unitize()

        # Calcular centroide
        centroid = rg.Point3d(
            (p1.X + p2.X + p3.X) / 3.0,
            (p1.Y + p2.Y + p3.Y) / 3.0,
            (p1.Z + p2.Z + p3.Z) / 3.0
        )

        # Crear superficie del panel
        panel_surface = self._create_triangular_surface(vertices)

        # Crear marco
        frame_brep = self._create_frame(vertices, normal)

        # Crear vidrio (offset hacia interior)
        glazing_vertices = self._offset_vertices(vertices, centroid)
        glazing_brep = self._create_glazing(glazing_vertices, normal)

        # Calcular area
        area = self._calculate_triangle_area(vertices)

        return PanelGeometry(
            index=face_index,
            brep=panel_surface,
            frame=frame_brep,
            glazing=glazing_brep,
            area=area,
            panel_type='triangle',
            vertices=vertices,
            normal=normal
        )

    def _create_triangular_surface(self, vertices):
        """Crea superficie triangular."""
        p1, p2, p3 = vertices

        # Crear mesh triangular
        mesh = rg.Mesh()
        mesh.Vertices.Add(p1)
        mesh.Vertices.Add(p2)
        mesh.Vertices.Add(p3)
        mesh.Faces.AddFace(0, 1, 2)
        mesh.Normals.ComputeNormals()

        # Convertir a Brep
        return rg.Brep.CreateFromMesh(mesh, False)

    def _create_frame(self, vertices, normal):
        """Crea marco del panel."""
        frames = []

        for i in range(3):
            start = vertices[i]
            end = vertices[(i + 1) % 3]

            # Crear perfil rectangular
            mid = rg.Point3d(
                (start.X + end.X) / 2.0,
                (start.Y + end.Y) / 2.0,
                (start.Z + end.Z) / 2.0
            )

            direction = rg.Vector3d(end - start)
            direction.Unitize()

            # Eje local perpendicular
            perp = rg.Vector3d.CrossProduct(direction, normal)
            perp.Unitize()

            # Crear rectangulo del perfil
            plane = rg.Plane(start, direction, perp)
            rect = rg.Rectangle3d(
                plane,
                rg.Interval(-self.frame_width / 2, self.frame_width / 2),
                rg.Interval(0, self.frame_depth)
            )

            profile = rect.ToNurbsCurve()

            # Extruir a lo largo del borde
            length = start.DistanceTo(end)
            extrusion = rg.Extrusion.Create(profile, length, True)

            if extrusion:
                frames.append(extrusion.ToBrep())

        # Unir marcos
        if frames:
            result = rg.Brep.CreateBooleanUnion(frames, 0.001)
            if result and len(result) > 0:
                return result[0]
            return frames[0]

        return None

    def _offset_vertices(self, vertices, centroid):
        """Calcula vertices con offset hacia el centro."""
        offset_vertices = []
        for v in vertices:
            direction = rg.Vector3d(centroid - v)
            direction.Unitize()
            offset_point = rg.Point3d(
                v.X + direction.X * self.glazing_offset,
                v.Y + direction.Y * self.glazing_offset,
                v.Z + direction.Z * self.glazing_offset
            )
            offset_vertices.append(offset_point)
        return offset_vertices

    def _create_glazing(self, vertices, normal):
        """Crea superficie de vidrio."""
        p1, p2, p3 = vertices

        # Crear superficie plana
        mesh = rg.Mesh()
        mesh.Vertices.Add(p1)
        mesh.Vertices.Add(p2)
        mesh.Vertices.Add(p3)
        mesh.Faces.AddFace(0, 1, 2)

        brep = rg.Brep.CreateFromMesh(mesh, False)

        if brep:
            # Extruir por espesor del material
            thickness = self.material.thickness / 1000.0  # mm a m

            # Mover hacia interior
            offset_vec = normal * (-thickness / 2)
            transform = rg.Transform.Translation(offset_vec)
            brep.Transform(transform)

        return brep

    def _calculate_triangle_area(self, vertices):
        """Calcula area del triangulo."""
        p1, p2, p3 = vertices
        a = p1.DistanceTo(p2)
        b = p2.DistanceTo(p3)
        c = p3.DistanceTo(p1)
        s = (a + b + c) / 2.0
        return math.sqrt(s * (s - a) * (s - b) * (s - c))


class HexagonalPanelBuilder:
    """Construye paneles hexagonales (Buckminster Fuller style)."""

    def __init__(self, frame_width=0.050, material='glass_single'):
        """
        Args:
            frame_width: Ancho del marco
            material: Material del panel
        """
        self.frame_width = frame_width
        self.material = PanelMaterialDatabase.get_material(material)

    def create_hexagonal_panels(self, geodesic_mesh):
        """
        Crea paneles hexagonales a partir de la malla geodesica.

        Los paneles hexagonales se forman uniendo los centroides
        de las caras triangulares adyacentes.

        Args:
            geodesic_mesh: GeodesicMesh

        Returns:
            list: Lista de PanelGeometry
        """
        # Mapear vertices a caras adyacentes
        vertex_to_faces = {}
        for face in geodesic_mesh.faces:
            for v_idx in face.vertices:
                if v_idx not in vertex_to_faces:
                    vertex_to_faces[v_idx] = []
                vertex_to_faces[v_idx].append(face)

        panels = []

        for vertex in geodesic_mesh.vertices:
            if vertex.type == 'base':
                continue  # Saltar vertices de base

            adjacent_faces = vertex_to_faces.get(vertex.index, [])

            if len(adjacent_faces) < 5:
                continue  # Necesitamos al menos 5 caras para hexagono

            # Ordenar caras por angulo alrededor del vertice
            center = vertex.point
            sorted_faces = self._sort_faces_around_vertex(
                adjacent_faces, center
            )

            # Obtener centroides
            centroids = [f.centroid for f in sorted_faces]

            if len(centroids) == 5:
                panel = self._build_pentagon(centroids, len(panels))
            elif len(centroids) >= 6:
                panel = self._build_hexagon(centroids[:6], len(panels))
            else:
                continue

            if panel:
                panels.append(panel)

        return panels

    def _sort_faces_around_vertex(self, faces, center):
        """Ordena caras por angulo alrededor del vertice."""
        def angle_key(face):
            direction = rg.Vector3d(face.centroid - center)
            return math.atan2(direction.Y, direction.X)

        return sorted(faces, key=angle_key)

    def _build_hexagon(self, vertices, index):
        """Construye panel hexagonal."""
        if len(vertices) != 6:
            return None

        # Crear poligono
        points = list(vertices) + [vertices[0]]
        polyline = rg.Polyline(points)
        curve = polyline.ToNurbsCurve()

        # Crear superficie
        breps = rg.Brep.CreatePlanarBreps(curve, 0.001)
        if not breps:
            return None

        brep = breps[0]

        # Calcular normal y area
        centroid = rg.Point3d(
            sum(v.X for v in vertices) / 6.0,
            sum(v.Y for v in vertices) / 6.0,
            sum(v.Z for v in vertices) / 6.0
        )

        normal = rg.Vector3d(centroid)
        normal.Unitize()

        # Area aproximada
        area = self._calculate_polygon_area(vertices)

        return PanelGeometry(
            index=index,
            brep=brep,
            frame=None,
            glazing=brep,
            area=area,
            panel_type='hexagon',
            vertices=vertices,
            normal=normal
        )

    def _build_pentagon(self, vertices, index):
        """Construye panel pentagonal."""
        if len(vertices) != 5:
            return None

        points = list(vertices) + [vertices[0]]
        polyline = rg.Polyline(points)
        curve = polyline.ToNurbsCurve()

        breps = rg.Brep.CreatePlanarBreps(curve, 0.001)
        if not breps:
            return None

        brep = breps[0]

        centroid = rg.Point3d(
            sum(v.X for v in vertices) / 5.0,
            sum(v.Y for v in vertices) / 5.0,
            sum(v.Z for v in vertices) / 5.0
        )

        normal = rg.Vector3d(centroid)
        normal.Unitize()

        area = self._calculate_polygon_area(vertices)

        return PanelGeometry(
            index=index,
            brep=brep,
            frame=None,
            glazing=brep,
            area=area,
            panel_type='pentagon',
            vertices=vertices,
            normal=normal
        )

    def _calculate_polygon_area(self, vertices):
        """Calcula area de poligono usando formula de shoelace 3D."""
        n = len(vertices)
        if n < 3:
            return 0.0

        # Para poligonos 3D, dividir en triangulos desde el centroide
        centroid = rg.Point3d(
            sum(v.X for v in vertices) / n,
            sum(v.Y for v in vertices) / n,
            sum(v.Z for v in vertices) / n
        )

        total_area = 0.0
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % n]

            # Area del triangulo
            a = centroid.DistanceTo(p1)
            b = p1.DistanceTo(p2)
            c = p2.DistanceTo(centroid)
            s = (a + b + c) / 2.0

            if s > a and s > b and s > c:
                area = math.sqrt(s * (s - a) * (s - b) * (s - c))
                total_area += area

        return total_area


class PanelAssemblyBuilder:
    """Construye el ensamble completo de paneles del domo."""

    def __init__(self, geodesic_mesh, panel_type='triangle',
                 material='glass_single'):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            panel_type: 'triangle', 'hexagon', 'mixed'
            material: Material del panel
        """
        self.mesh = geodesic_mesh
        self.panel_type = panel_type
        self.material = material

        self.triangle_builder = TriangularPanelBuilder(material=material)
        self.hexagon_builder = HexagonalPanelBuilder(material=material)

    def build_triangular_panels(self):
        """
        Construye todos los paneles triangulares.

        Returns:
            list: Lista de PanelGeometry
        """
        panels = []

        for face in self.mesh.faces:
            vertices = [
                self.mesh.vertices[v_idx].point
                for v_idx in face.vertices
            ]

            panel = self.triangle_builder.build_panel(vertices, face.index)
            if panel:
                panels.append(panel)

        return panels

    def build_hexagonal_panels(self):
        """
        Construye paneles hexagonales.

        Returns:
            list: Lista de PanelGeometry
        """
        return self.hexagon_builder.create_hexagonal_panels(self.mesh)

    def build_all_panels(self):
        """
        Construye todos los paneles segun el tipo especificado.

        Returns:
            list: Lista de PanelGeometry
        """
        if self.panel_type == 'triangle':
            return self.build_triangular_panels()
        elif self.panel_type == 'hexagon':
            return self.build_hexagonal_panels()
        elif self.panel_type == 'mixed':
            # Combinar ambos tipos
            triangles = self.build_triangular_panels()
            hexagons = self.build_hexagonal_panels()
            return triangles + hexagons
        else:
            return self.build_triangular_panels()

    def get_panel_schedule(self):
        """
        Genera tabla de paneles para fabricacion.

        Returns:
            dict: Resumen de paneles
        """
        panels = self.build_all_panels()

        # Agrupar por tipo
        by_type = {}
        for panel in panels:
            t = panel.panel_type
            if t not in by_type:
                by_type[t] = {'count': 0, 'total_area': 0.0}
            by_type[t]['count'] += 1
            by_type[t]['total_area'] += panel.area

        # Agregar costos
        material = PanelMaterialDatabase.get_material(self.material)

        for t, data in by_type.items():
            data['material'] = material.name
            data['cost'] = data['total_area'] * material.cost_per_m2
            data['weight'] = (data['total_area'] *
                              material.thickness / 1000.0 *
                              material.density)

        return by_type


class GlazingSystemBuilder:
    """Construye sistemas de acristalamiento especializados."""

    def __init__(self, system_type='stick', mullion_profile='50x80'):
        """
        Args:
            system_type: 'stick', 'unitized', 'structural'
            mullion_profile: Perfil de montante
        """
        self.system_type = system_type
        self.mullion_profile = mullion_profile

    def build_mullion_grid(self, geodesic_mesh, mullion_width=0.050):
        """
        Construye rejilla de montantes.

        Args:
            geodesic_mesh: GeodesicMesh
            mullion_width: Ancho del montante

        Returns:
            list: Lista de curvas de montantes
        """
        mullions = []

        for edge in geodesic_mesh.edges:
            start = geodesic_mesh.vertices[edge.start].point
            end = geodesic_mesh.vertices[edge.end].point

            # Crear linea del montante
            mullion_curve = rg.LineCurve(start, end)
            mullions.append(mullion_curve)

        return mullions

    def build_pressure_plates(self, geodesic_mesh, plate_width=0.030):
        """
        Construye tapajuntas de presion.

        Args:
            geodesic_mesh: GeodesicMesh
            plate_width: Ancho del tapajuntas

        Returns:
            list: Lista de Brep
        """
        plates = []

        for edge in geodesic_mesh.edges:
            start = geodesic_mesh.vertices[edge.start].point
            end = geodesic_mesh.vertices[edge.end].point

            # Direccion del borde
            direction = rg.Vector3d(end - start)
            direction.Unitize()

            # Normal hacia afuera
            mid = rg.Point3d(
                (start.X + end.X) / 2.0,
                (start.Y + end.Y) / 2.0,
                (start.Z + end.Z) / 2.0
            )
            normal = rg.Vector3d(mid)
            normal.Unitize()

            # Eje lateral
            lateral = rg.Vector3d.CrossProduct(direction, normal)
            lateral.Unitize()

            # Crear perfil del tapajuntas
            plane = rg.Plane(start, direction, lateral)
            rect = rg.Rectangle3d(
                plane,
                rg.Interval(-plate_width / 2, plate_width / 2),
                rg.Interval(0, 0.010)  # 10mm de alto
            )

            profile = rect.ToNurbsCurve()
            length = start.DistanceTo(end)
            extrusion = rg.Extrusion.Create(profile, length, True)

            if extrusion:
                brep = extrusion.ToBrep()

                # Mover hacia afuera
                offset = normal * 0.005
                transform = rg.Transform.Translation(offset)
                brep.Transform(transform)

                plates.append(brep)

        return plates


class SealingSystemBuilder:
    """Construye sistema de sellado y juntas."""

    def __init__(self, gasket_width=0.020):
        """
        Args:
            gasket_width: Ancho del empaque
        """
        self.gasket_width = gasket_width

    def create_perimeter_gasket(self, panel_vertices):
        """
        Crea empaque perimetral del panel.

        Args:
            panel_vertices: Vertices del panel

        Returns:
            Curve: Curva del empaque
        """
        # Crear polilinea cerrada
        points = list(panel_vertices) + [panel_vertices[0]]
        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def create_gasket_profile(self, curve, profile_type='EPDM'):
        """
        Crea perfil 3D del empaque.

        Args:
            curve: Curva base
            profile_type: Tipo de perfil

        Returns:
            Brep: Empaque 3D
        """
        if profile_type == 'EPDM':
            # Perfil circular
            start = curve.PointAtStart
            direction = curve.TangentAtStart
            perp = rg.Vector3d(start)
            perp.Unitize()

            plane = rg.Plane(start, direction)
            circle = rg.Circle(plane, self.gasket_width / 2)
            profile = circle.ToNurbsCurve()

            sweep = rg.SweepOneRail()
            breps = sweep.PerformSweep(curve, profile)

            if breps and len(breps) > 0:
                return breps[0]

        return None


# Funciones de utilidad
def create_panel_surfaces(geodesic_mesh):
    """
    Crea superficies simples para visualizacion rapida.

    Args:
        geodesic_mesh: GeodesicMesh

    Returns:
        Mesh: Malla de superficies
    """
    mesh = rg.Mesh()

    for vertex in geodesic_mesh.vertices:
        mesh.Vertices.Add(vertex.point)

    for face in geodesic_mesh.faces:
        mesh.Faces.AddFace(
            face.vertices[0],
            face.vertices[1],
            face.vertices[2]
        )

    mesh.Normals.ComputeNormals()
    mesh.Compact()

    return mesh


def get_panel_statistics(panels):
    """
    Obtiene estadisticas de los paneles.

    Args:
        panels: Lista de PanelGeometry

    Returns:
        dict: Estadisticas
    """
    total_area = sum(p.area for p in panels)
    areas = [p.area for p in panels]

    return {
        'count': len(panels),
        'total_area_m2': total_area,
        'min_area_m2': min(areas) if areas else 0,
        'max_area_m2': max(areas) if areas else 0,
        'avg_area_m2': total_area / len(panels) if panels else 0
    }


# Ejemplo de uso
if __name__ == "__main__":
    from geodesic_generator import GeodesicDomeGenerator

    # Generar domo
    generator = GeodesicDomeGenerator()
    mesh = generator.generate(radius=10.0, frequency=3, truncation=0.5)

    # Construir paneles triangulares
    panel_builder = PanelAssemblyBuilder(
        mesh, panel_type='triangle', material='glass_double'
    )

    schedule = panel_builder.get_panel_schedule()
    print("Paneles:")
    for panel_type, data in schedule.items():
        print(f"  {panel_type}: {data['count']} unidades, "
              f"{data['total_area']:.1f} m2, ${data['cost']:.0f}")
