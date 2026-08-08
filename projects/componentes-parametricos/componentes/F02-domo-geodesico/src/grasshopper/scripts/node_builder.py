#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Nodos - F02 Domo Geodesico Parametrico

Genera la geometria de nodos (hubs) para conexion de barras
en domos geodesicos.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
NodeGeometry = namedtuple('NodeGeometry', [
    'index', 'brep', 'center', 'type', 'connections',
    'connection_angles', 'is_base'
])

ConnectionPort = namedtuple('ConnectionPort', [
    'direction', 'angle_from_vertical', 'strut_index'
])


class NodeAnalyzer:
    """Analiza conectividad de nodos en la malla geodesica."""

    def __init__(self, geodesic_mesh):
        """
        Args:
            geodesic_mesh: GeodesicMesh del generador
        """
        self.mesh = geodesic_mesh
        self.node_connections = {}
        self._analyze_connections()

    def _analyze_connections(self):
        """Analiza conexiones de cada nodo."""
        for vertex in self.mesh.vertices:
            self.node_connections[vertex.index] = []

        for edge in self.mesh.edges:
            # Agregar conexion bidireccional
            self.node_connections[edge.start].append({
                'edge_index': edge.index,
                'other_node': edge.end,
                'chord_type': edge.chord_type
            })
            self.node_connections[edge.end].append({
                'edge_index': edge.index,
                'other_node': edge.start,
                'chord_type': edge.chord_type
            })

    def get_node_valence(self, node_index):
        """Obtiene numero de conexiones del nodo."""
        return len(self.node_connections.get(node_index, []))

    def get_connection_directions(self, node_index):
        """
        Obtiene direcciones de conexion del nodo.

        Args:
            node_index: Indice del nodo

        Returns:
            list: Lista de ConnectionPort
        """
        vertex = self.mesh.vertices[node_index]
        center = vertex.point

        directions = []
        for conn in self.node_connections[node_index]:
            other = self.mesh.vertices[conn['other_node']]
            direction = rg.Vector3d(other.point - center)
            direction.Unitize()

            # Calcular angulo desde vertical
            vertical = rg.Vector3d(0, 0, 1)
            angle = rg.Vector3d.VectorAngle(direction, vertical)

            directions.append(ConnectionPort(
                direction=direction,
                angle_from_vertical=math.degrees(angle),
                strut_index=conn['edge_index']
            ))

        return directions

    def get_statistics(self):
        """Obtiene estadisticas de nodos."""
        valences = {}
        for node_idx in self.node_connections:
            v = self.get_node_valence(node_idx)
            valences[v] = valences.get(v, 0) + 1

        return valences


class SphericalNodeBuilder:
    """Construye nodos esfericos (hub type)."""

    def __init__(self, base_radius=0.05, wall_thickness=0.008):
        """
        Args:
            base_radius: Radio base del nodo en metros
            wall_thickness: Espesor de pared
        """
        self.base_radius = base_radius
        self.wall_thickness = wall_thickness

    def build_solid_sphere(self, center, radius=None):
        """
        Construye nodo esferico solido.

        Args:
            center: Centro del nodo
            radius: Radio (usa base_radius si no se especifica)

        Returns:
            Brep: Esfera
        """
        r = radius or self.base_radius
        sphere = rg.Sphere(center, r)
        return rg.Brep.CreateFromSphere(sphere)

    def build_hollow_sphere(self, center, radius=None):
        """
        Construye nodo esferico hueco.

        Args:
            center: Centro del nodo
            radius: Radio exterior

        Returns:
            Brep: Esfera hueca
        """
        r = radius or self.base_radius
        outer = rg.Sphere(center, r)
        inner = rg.Sphere(center, r - self.wall_thickness)

        outer_brep = rg.Brep.CreateFromSphere(outer)
        inner_brep = rg.Brep.CreateFromSphere(inner)

        result = rg.Brep.CreateBooleanDifference(
            outer_brep, inner_brep, 0.001
        )

        if result and len(result) > 0:
            return result[0]
        return outer_brep

    def build_with_ports(self, center, connection_directions, radius=None):
        """
        Construye nodo con puertos para barras.

        Args:
            center: Centro del nodo
            connection_directions: Lista de ConnectionPort
            radius: Radio del nodo

        Returns:
            Brep: Nodo con puertos
        """
        r = radius or self.base_radius

        # Crear esfera base
        node_brep = self.build_solid_sphere(center, r)

        if not connection_directions:
            return node_brep

        # Crear cilindros para puertos
        port_radius = r * 0.4  # Radio del puerto
        port_depth = r * 0.8  # Profundidad

        for port in connection_directions:
            # Punto de inicio del cilindro (interior del nodo)
            start = rg.Point3d(
                center.X + port.direction.X * (r - port_depth),
                center.Y + port.direction.Y * (r - port_depth),
                center.Z + port.direction.Z * (r - port_depth)
            )

            # Punto final (exterior)
            end = rg.Point3d(
                center.X + port.direction.X * (r + 0.01),
                center.Y + port.direction.Y * (r + 0.01),
                center.Z + port.direction.Z * (r + 0.01)
            )

            # Crear cilindro
            plane = rg.Plane(start, port.direction)
            circle = rg.Circle(plane, port_radius)
            cylinder = rg.Cylinder(circle, start.DistanceTo(end))
            cyl_brep = rg.Brep.CreateFromCylinder(cylinder, True, True)

            if cyl_brep:
                result = rg.Brep.CreateBooleanDifference(
                    node_brep, cyl_brep, 0.001
                )
                if result and len(result) > 0:
                    node_brep = result[0]

        return node_brep


class PlateNodeBuilder:
    """Construye nodos tipo placa (gusset plates)."""

    def __init__(self, plate_thickness=0.010):
        """
        Args:
            plate_thickness: Espesor de placa en metros
        """
        self.plate_thickness = plate_thickness

    def build_plate_node(self, center, connection_directions, plate_size=0.1):
        """
        Construye nodo de placas soldadas.

        Args:
            center: Centro del nodo
            connection_directions: Lista de ConnectionPort
            plate_size: Tamano de placa

        Returns:
            list: Lista de Brep (placas)
        """
        plates = []

        if not connection_directions:
            return plates

        # Crear una placa por cada par de conexiones adyacentes
        n = len(connection_directions)

        for i in range(n):
            dir1 = connection_directions[i].direction
            dir2 = connection_directions[(i + 1) % n].direction

            # Normal de la placa (perpendicular a ambas direcciones)
            normal = rg.Vector3d.CrossProduct(dir1, dir2)
            if normal.Length < 0.001:
                continue
            normal.Unitize()

            # Crear plano de la placa
            plane = rg.Plane(center, normal)

            # Crear contorno de la placa
            points = [
                center,
                rg.Point3d(
                    center.X + dir1.X * plate_size,
                    center.Y + dir1.Y * plate_size,
                    center.Z + dir1.Z * plate_size
                ),
                rg.Point3d(
                    center.X + (dir1.X + dir2.X) * plate_size * 0.7,
                    center.Y + (dir1.Y + dir2.Y) * plate_size * 0.7,
                    center.Z + (dir1.Z + dir2.Z) * plate_size * 0.7
                ),
                rg.Point3d(
                    center.X + dir2.X * plate_size,
                    center.Y + dir2.Y * plate_size,
                    center.Z + dir2.Z * plate_size
                )
            ]

            polyline = rg.Polyline(points + [points[0]])
            curve = polyline.ToNurbsCurve()

            # Extruir
            extrusion_vec = normal * self.plate_thickness
            extrusion = rg.Extrusion.Create(
                curve, self.plate_thickness, True
            )

            if extrusion:
                plates.append(extrusion.ToBrep())

        return plates


class FlattenedEndNodeBuilder:
    """Construye nodos tipo extremo aplastado (bolt-through)."""

    def __init__(self, flattened_width=0.06, bolt_diameter=0.016):
        """
        Args:
            flattened_width: Ancho del aplastado
            bolt_diameter: Diametro del perno
        """
        self.flattened_width = flattened_width
        self.bolt_diameter = bolt_diameter

    def build_flattened_end(self, strut_end, direction, strut_radius):
        """
        Construye extremo aplastado de una barra.

        Args:
            strut_end: Punto final de la barra
            direction: Direccion de la barra
            strut_radius: Radio de la barra

        Returns:
            Brep: Geometria del extremo aplastado
        """
        # Crear placa aplastada
        width = self.flattened_width
        height = strut_radius * 2
        length = width * 1.5

        # Plano perpendicular a la direccion
        plane = rg.Plane(strut_end, direction)

        # Crear rectangulo
        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-width / 2, width / 2),
            rg.Interval(-height / 2, height / 2)
        )

        # Extruir
        profile = rect.ToNurbsCurve()
        extrusion = rg.Extrusion.Create(profile, length, True)

        if extrusion:
            plate = extrusion.ToBrep()

            # Crear agujero para perno
            hole_center = rg.Point3d(
                strut_end.X + direction.X * length / 2,
                strut_end.Y + direction.Y * length / 2,
                strut_end.Z + direction.Z * length / 2
            )

            hole_plane = rg.Plane(
                rg.Point3d(
                    hole_center.X,
                    hole_center.Y - height,
                    hole_center.Z
                ),
                rg.Vector3d(0, 1, 0)
            )

            hole_circle = rg.Circle(hole_plane, self.bolt_diameter / 2)
            hole_cyl = rg.Cylinder(hole_circle, height * 2)
            hole_brep = rg.Brep.CreateFromCylinder(hole_cyl, True, True)

            if hole_brep:
                result = rg.Brep.CreateBooleanDifference(
                    plate, hole_brep, 0.001
                )
                if result and len(result) > 0:
                    return result[0]

            return plate

        return None


class NodeAssemblyBuilder:
    """Construye el ensamble completo de nodos del domo."""

    def __init__(self, geodesic_mesh, node_type='spherical',
                 node_radius=0.05):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            node_type: 'spherical', 'plate', 'flattened'
            node_radius: Radio base del nodo
        """
        self.mesh = geodesic_mesh
        self.node_type = node_type
        self.node_radius = node_radius
        self.analyzer = NodeAnalyzer(geodesic_mesh)

        # Builders
        self.sphere_builder = SphericalNodeBuilder(node_radius)
        self.plate_builder = PlateNodeBuilder()
        self.flat_builder = FlattenedEndNodeBuilder()

    def build_node(self, vertex_index):
        """
        Construye un nodo individual.

        Args:
            vertex_index: Indice del vertice

        Returns:
            NodeGeometry
        """
        vertex = self.mesh.vertices[vertex_index]
        center = vertex.point
        is_base = vertex.type == 'base'

        connections = self.analyzer.get_connection_directions(vertex_index)

        if self.node_type == 'spherical':
            # Ajustar radio segun numero de conexiones
            valence = len(connections)
            radius = self.node_radius * (1.0 + valence * 0.05)

            brep = self.sphere_builder.build_with_ports(
                center, connections, radius
            )

        elif self.node_type == 'plate':
            breps = self.plate_builder.build_plate_node(
                center, connections
            )
            # Unir placas
            if breps:
                brep = breps[0]
                for b in breps[1:]:
                    result = rg.Brep.CreateBooleanUnion([brep, b], 0.001)
                    if result and len(result) > 0:
                        brep = result[0]
            else:
                brep = self.sphere_builder.build_solid_sphere(center)

        else:  # simplified
            brep = self.sphere_builder.build_solid_sphere(center)

        # Calcular angulos de conexion
        angles = [c.angle_from_vertical for c in connections]

        return NodeGeometry(
            index=vertex_index,
            brep=brep,
            center=center,
            type=self.node_type,
            connections=len(connections),
            connection_angles=angles,
            is_base=is_base
        )

    def build_all_nodes(self):
        """
        Construye todos los nodos del domo.

        Returns:
            list: Lista de NodeGeometry
        """
        nodes = []
        for vertex in self.mesh.vertices:
            node = self.build_node(vertex.index)
            nodes.append(node)
        return nodes

    def build_base_nodes_only(self):
        """
        Construye solo los nodos de la base.

        Returns:
            list: Lista de NodeGeometry
        """
        nodes = []
        for vertex in self.mesh.vertices:
            if vertex.type == 'base':
                node = self.build_node(vertex.index)
                nodes.append(node)
        return nodes

    def get_node_schedule(self):
        """
        Genera tabla de nodos para fabricacion.

        Returns:
            list: Lista de dicts con informacion de nodos
        """
        stats = self.analyzer.get_statistics()

        schedule = []
        for valence, count in sorted(stats.items()):
            schedule.append({
                'valence': valence,
                'quantity': count,
                'type': self.node_type,
                'radius': self.node_radius * (1.0 + valence * 0.05),
                'description': f"Nodo {valence}-way"
            })

        return schedule


class BaseConnectionBuilder:
    """Construye conexiones de base del domo."""

    def __init__(self, geodesic_mesh, base_plate_size=0.2,
                 base_plate_thickness=0.020):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            base_plate_size: Tamano de placa base
            base_plate_thickness: Espesor de placa base
        """
        self.mesh = geodesic_mesh
        self.plate_size = base_plate_size
        self.plate_thickness = base_plate_thickness

    def build_base_plate(self, node_center, anchor_pattern='4_bolt'):
        """
        Construye placa base para anclaje.

        Args:
            node_center: Centro del nodo de base
            anchor_pattern: Patron de anclajes

        Returns:
            Brep: Placa base con agujeros
        """
        # Proyectar al piso
        base_center = rg.Point3d(node_center.X, node_center.Y, 0)

        # Crear placa cuadrada
        plane = rg.Plane(base_center, rg.Vector3d.ZAxis)
        half_size = self.plate_size / 2

        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-half_size, half_size),
            rg.Interval(-half_size, half_size)
        )

        profile = rect.ToNurbsCurve()
        extrusion = rg.Extrusion.Create(profile, self.plate_thickness, True)

        if not extrusion:
            return None

        plate = extrusion.ToBrep()

        # Agregar agujeros de anclaje
        if anchor_pattern == '4_bolt':
            bolt_positions = [
                (-half_size * 0.6, -half_size * 0.6),
                (half_size * 0.6, -half_size * 0.6),
                (half_size * 0.6, half_size * 0.6),
                (-half_size * 0.6, half_size * 0.6)
            ]
        else:
            bolt_positions = [(0, 0)]

        bolt_diameter = 0.020  # 20mm

        for bx, by in bolt_positions:
            hole_center = rg.Point3d(
                base_center.X + bx,
                base_center.Y + by,
                base_center.Z - 0.01
            )

            hole_plane = rg.Plane(hole_center, rg.Vector3d.ZAxis)
            hole_circle = rg.Circle(hole_plane, bolt_diameter / 2)
            hole_cyl = rg.Cylinder(hole_circle, self.plate_thickness + 0.02)
            hole_brep = rg.Brep.CreateFromCylinder(hole_cyl, True, True)

            if hole_brep:
                result = rg.Brep.CreateBooleanDifference(
                    plate, hole_brep, 0.001
                )
                if result and len(result) > 0:
                    plate = result[0]

        return plate

    def build_all_base_plates(self):
        """
        Construye todas las placas base.

        Returns:
            list: Lista de Brep
        """
        plates = []
        for vertex in self.mesh.vertices:
            if vertex.type == 'base':
                plate = self.build_base_plate(vertex.point)
                if plate:
                    plates.append(plate)
        return plates


# Funciones de utilidad
def create_node_points(geodesic_mesh):
    """
    Crea puntos de nodos para visualizacion.

    Args:
        geodesic_mesh: GeodesicMesh

    Returns:
        list: Lista de Point3d
    """
    return [v.point for v in geodesic_mesh.vertices]


def create_node_spheres(geodesic_mesh, radius=0.05):
    """
    Crea esferas simples para visualizacion de nodos.

    Args:
        geodesic_mesh: GeodesicMesh
        radius: Radio de las esferas

    Returns:
        list: Lista de Brep
    """
    spheres = []
    for vertex in geodesic_mesh.vertices:
        sphere = rg.Sphere(vertex.point, radius)
        brep = rg.Brep.CreateFromSphere(sphere)
        spheres.append(brep)
    return spheres


# Ejemplo de uso
if __name__ == "__main__":
    from geodesic_generator import GeodesicDomeGenerator

    # Generar domo
    generator = GeodesicDomeGenerator()
    mesh = generator.generate(radius=10.0, frequency=3, truncation=0.5)

    # Construir nodos
    node_builder = NodeAssemblyBuilder(
        mesh, node_type='spherical', node_radius=0.08
    )

    # Tabla de nodos
    schedule = node_builder.get_node_schedule()
    print("Tabla de nodos:")
    for item in schedule:
        print(f"  {item['description']}: {item['quantity']} unidades")

    # Construir todos
    nodes = node_builder.build_all_nodes()
    print(f"\nTotal nodos construidos: {len(nodes)}")
