"""
Node Builder - Cercha Parametrica
Genera nodos y conexiones para la cercha.

Inputs:
    nodes (List[Point3d]): Puntos de nodos
    node_data (List[NodeData]): Datos de nodos
    member_data (List[MemberData]): Datos de miembros
    profile_results (List[SelectionResult]): Perfiles seleccionados
    connection_type (str): Tipo de conexion (welded/bolted/pinned)
    gusset_thickness (float): Espesor de placa (mm)

Outputs:
    gusset_plates (List[Brep]): Placas de nodo
    welds (List[Line]): Lineas de soldadura
    bolts (List[Point3d]): Posiciones de tornillos
    connection_data (List[dict]): Datos de cada conexion
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de conexion
ConnectionData = namedtuple('ConnectionData', [
    'node_id', 'type', 'gusset_plate', 'member_count',
    'weld_length', 'bolt_count', 'capacity', 'utilization'
])

# Datos de soldadura
WeldData = namedtuple('WeldData', [
    'line', 'size', 'length', 'type', 'capacity'
])

# Resultado del constructor de nodos
NodeResult = namedtuple('NodeResult', [
    'gusset_plates', 'welds', 'bolts', 'stiffeners',
    'connection_data', 'total_weld_length', 'total_bolt_count'
])


class WeldCalculator:
    """Calcula soldaduras segun AWS D1.1."""

    # Electrodos comunes
    ELECTRODES = {
        'E70XX': {'Fexx': 482},  # MPa
        'E60XX': {'Fexx': 413},
        'E80XX': {'Fexx': 551},
    }

    def __init__(self, electrode='E70XX'):
        self.electrode = self.ELECTRODES.get(electrode, self.ELECTRODES['E70XX'])
        self.Fexx = self.electrode['Fexx']
        self.phi = 0.75  # Factor de resistencia

    def calculate_fillet_weld(self, size_mm, length_mm):
        """
        Calcula capacidad de soldadura de filete.

        Args:
            size_mm: Tamano de filete (mm)
            length_mm: Longitud de soldadura (mm)

        Returns:
            float: Capacidad en kN
        """
        # Area efectiva de garganta
        throat = 0.707 * size_mm  # mm
        Aw = throat * length_mm   # mm2

        # Resistencia nominal
        Fnw = 0.60 * self.Fexx  # MPa

        # Capacidad
        Rn = Fnw * Aw / 1000  # kN

        return self.phi * Rn

    def required_weld_length(self, force_kN, size_mm):
        """
        Calcula longitud de soldadura requerida.

        Args:
            force_kN: Fuerza a transmitir (kN)
            size_mm: Tamano de filete (mm)

        Returns:
            float: Longitud requerida (mm)
        """
        throat = 0.707 * size_mm
        Fnw = 0.60 * self.Fexx

        # L = P / (phi * Fnw * throat)
        L = (force_kN * 1000) / (self.phi * Fnw * throat)

        return L

    def minimum_weld_size(self, thickness_mm):
        """
        Determina tamano minimo de soldadura segun AWS.

        Args:
            thickness_mm: Espesor del material mas grueso

        Returns:
            float: Tamano minimo de filete (mm)
        """
        if thickness_mm <= 6:
            return 3
        elif thickness_mm <= 13:
            return 5
        elif thickness_mm <= 19:
            return 6
        else:
            return 8


class BoltCalculator:
    """Calcula conexiones atornilladas segun AISC."""

    # Tornillos de alta resistencia
    BOLT_GRADES = {
        'A325': {
            'Fnv': 372,  # MPa (cortante, rosca excluida)
            'Fnt': 620,  # MPa (tension)
        },
        'A490': {
            'Fnv': 457,
            'Fnt': 780,
        },
    }

    # Diametros estandar
    BOLT_DIAMETERS = [16, 20, 22, 24, 27, 30]  # mm

    def __init__(self, grade='A325'):
        self.grade = self.BOLT_GRADES.get(grade, self.BOLT_GRADES['A325'])
        self.Fnv = self.grade['Fnv']
        self.Fnt = self.grade['Fnt']
        self.phi_shear = 0.75
        self.phi_tension = 0.75
        self.phi_bearing = 0.75

    def shear_capacity(self, diameter_mm, n_shear_planes=1):
        """
        Calcula capacidad a cortante de un tornillo.

        Args:
            diameter_mm: Diametro del tornillo (mm)
            n_shear_planes: Numero de planos de corte

        Returns:
            float: Capacidad en kN
        """
        Ab = math.pi * (diameter_mm ** 2) / 4  # mm2
        Rn = self.Fnv * Ab * n_shear_planes / 1000  # kN

        return self.phi_shear * Rn

    def bearing_capacity(self, diameter_mm, plate_thickness, Fu=400):
        """
        Calcula capacidad por aplastamiento.

        Args:
            diameter_mm: Diametro del tornillo (mm)
            plate_thickness: Espesor de placa (mm)
            Fu: Resistencia ultima del material (MPa)

        Returns:
            float: Capacidad en kN
        """
        # Aplastamiento en borde de agujero
        Rn = 2.4 * diameter_mm * plate_thickness * Fu / 1000  # kN

        return self.phi_bearing * Rn

    def required_bolts(self, force_kN, diameter_mm, plate_thickness):
        """
        Calcula numero de tornillos requeridos.

        Args:
            force_kN: Fuerza a transmitir (kN)
            diameter_mm: Diametro del tornillo (mm)
            plate_thickness: Espesor de placa (mm)

        Returns:
            int: Numero de tornillos
        """
        shear_cap = self.shear_capacity(diameter_mm)
        bearing_cap = self.bearing_capacity(diameter_mm, plate_thickness)

        # Capacidad gobernante
        cap_per_bolt = min(shear_cap, bearing_cap)

        n_bolts = math.ceil(force_kN / cap_per_bolt)

        return max(2, n_bolts)  # Minimo 2 tornillos

    def edge_distance(self, diameter_mm):
        """Distancia minima al borde."""
        return 1.5 * diameter_mm

    def spacing(self, diameter_mm):
        """Espaciamiento minimo entre tornillos."""
        return 3 * diameter_mm


class GussetPlateDesigner:
    """Disena placas de nodo (gussets)."""

    def __init__(self, material_Fy=250, material_Fu=400):
        self.Fy = material_Fy  # MPa
        self.Fu = material_Fu  # MPa
        self.phi = 0.90

    def design_gusset(self, node_data, connected_members, profile_results):
        """
        Disena una placa de nodo.

        Args:
            node_data: Datos del nodo
            connected_members: Miembros conectados
            profile_results: Perfiles de los miembros

        Returns:
            dict: Diseno de la placa
        """
        # Encontrar el perfil mas grande
        max_dimension = 0
        for member in connected_members:
            for result in profile_results:
                if result.member_id == member.id:
                    dim = max(result.profile.dimensions[:2])
                    max_dimension = max(max_dimension, dim)

        # Calcular tamano de placa
        # La placa debe extenderse para acomodar soldaduras
        weld_length_required = 150  # mm estimado

        # Radio de la placa (distancia del centro al borde)
        radius = max_dimension / 2 + weld_length_required + 50

        # Espesor basado en miembros conectados
        # Regla: espesor >= espesor mas grueso de miembro / 2
        max_thickness = 0
        for member in connected_members:
            for result in profile_results:
                if result.member_id == member.id:
                    t = result.profile.dimensions[2] if len(result.profile.dimensions) > 2 else 6
                    max_thickness = max(max_thickness, t)

        thickness = max(10, max_thickness)

        return {
            'radius': radius,
            'thickness': thickness,
            'shape': 'circular' if len(connected_members) > 4 else 'polygon',
            'center': node_data.point,
            'member_count': len(connected_members)
        }


class NodeBuilder:
    """Constructor de nodos y conexiones."""

    def __init__(self, connection_type='welded', gusset_thickness=12):
        """
        Args:
            connection_type: 'welded', 'bolted', o 'pinned'
            gusset_thickness: Espesor de placa (mm)
        """
        self.connection_type = connection_type
        self.gusset_thickness = gusset_thickness
        self.weld_calc = WeldCalculator()
        self.bolt_calc = BoltCalculator()
        self.gusset_designer = GussetPlateDesigner()
        self.tolerance = 0.001

    def build(self, nodes, node_data, member_data, profile_results):
        """
        Construye todas las conexiones.

        Args:
            nodes: Lista de puntos de nodos
            node_data: Lista de NodeData
            member_data: Lista de MemberData
            profile_results: Lista de SelectionResult

        Returns:
            NodeResult
        """
        gusset_plates = []
        welds = []
        bolts = []
        stiffeners = []
        connection_data = []

        total_weld_length = 0
        total_bolt_count = 0

        for i, nd in enumerate(node_data):
            # Encontrar miembros conectados a este nodo
            connected = self._find_connected_members(nd, member_data)

            if len(connected) < 2:
                continue  # No es un nodo de conexion

            # Diseniar placa de nodo
            gusset_design = self.gusset_designer.design_gusset(
                nd, connected, profile_results
            )

            # Crear geometria de placa
            gusset_brep = self._create_gusset_geometry(gusset_design, nd, connected)
            if gusset_brep:
                gusset_plates.append(gusset_brep)

            # Crear conexiones segun tipo
            if self.connection_type == 'welded':
                node_welds = self._create_welded_connections(nd, connected, profile_results)
                welds.extend(node_welds)
                total_weld_length += sum(w.length for w in node_welds)

            elif self.connection_type == 'bolted':
                node_bolts = self._create_bolted_connections(nd, connected, profile_results)
                bolts.extend(node_bolts)
                total_bolt_count += len(node_bolts)

            # Crear datos de conexion
            conn_data = self._create_connection_data(
                nd, connected, gusset_design,
                welds if self.connection_type == 'welded' else [],
                bolts if self.connection_type == 'bolted' else []
            )
            connection_data.append(conn_data)

        return NodeResult(
            gusset_plates=gusset_plates,
            welds=[w.line for w in welds] if welds else [],
            bolts=bolts,
            stiffeners=stiffeners,
            connection_data=connection_data,
            total_weld_length=total_weld_length,
            total_bolt_count=total_bolt_count
        )

    def _find_connected_members(self, node_data, member_data):
        """Encuentra miembros conectados a un nodo."""
        connected = []
        node_point = node_data.point

        for member in member_data:
            start = member.line.From
            end = member.line.To

            # Verificar si el miembro esta conectado al nodo
            dist_start = start.DistanceTo(node_point)
            dist_end = end.DistanceTo(node_point)

            if dist_start < 1.0 or dist_end < 1.0:  # Tolerancia de 1mm
                connected.append(member)

        return connected

    def _create_gusset_geometry(self, design, node_data, connected_members):
        """Crea la geometria 3D de la placa de nodo."""
        center = node_data.point
        radius = design['radius']
        thickness = design['thickness']

        if design['shape'] == 'circular':
            # Placa circular
            circle = rg.Circle(
                rg.Plane(center, rg.Vector3d.ZAxis),
                radius
            )
            disk = rg.Brep.CreatePlanarBreps(
                circle.ToNurbsCurve(),
                self.tolerance
            )
            if disk:
                # Extruir
                extrusion = rg.Extrusion.Create(
                    circle.ToNurbsCurve(),
                    thickness,
                    True
                )
                return extrusion.ToBrep() if extrusion else disk[0]

        else:
            # Placa poligonal basada en miembros
            return self._create_polygon_gusset(center, connected_members, radius, thickness)

        return None

    def _create_polygon_gusset(self, center, members, radius, thickness):
        """Crea placa de nodo poligonal."""
        # Encontrar direcciones de miembros
        directions = []
        for member in members:
            line = member.line
            if center.DistanceTo(line.From) < 1.0:
                direction = rg.Vector3d(line.To - center)
            else:
                direction = rg.Vector3d(line.From - center)
            direction.Unitize()
            directions.append(direction)

        if len(directions) < 3:
            # Fallback a circular
            circle = rg.Circle(rg.Plane(center, rg.Vector3d.ZAxis), radius)
            extrusion = rg.Extrusion.Create(circle.ToNurbsCurve(), thickness, True)
            return extrusion.ToBrep() if extrusion else None

        # Crear puntos del poligono
        points = []
        for d in directions:
            pt = center + d * radius
            points.append(pt)
        points.append(points[0])  # Cerrar

        # Crear polyline
        polyline = rg.Polyline(points)
        curve = polyline.ToNurbsCurve()

        # Extruir
        extrusion = rg.Extrusion.Create(curve, thickness, True)
        return extrusion.ToBrep() if extrusion else None

    def _create_welded_connections(self, node_data, connected_members, profile_results):
        """Crea soldaduras para conexion soldada."""
        welds = []
        center = node_data.point

        for member in connected_members:
            # Encontrar perfil del miembro
            profile = None
            for pr in profile_results:
                if pr.member_id == member.id:
                    profile = pr.profile
                    break

            if profile is None:
                continue

            # Determinar tamano de soldadura
            member_thickness = profile.dimensions[2] if len(profile.dimensions) > 2 else 6
            weld_size = self.weld_calc.minimum_weld_size(
                max(member_thickness, self.gusset_thickness)
            )

            # Longitud de soldadura = perimetro del perfil * factor
            if profile.type == 'HSS':
                perimeter = 2 * (profile.dimensions[0] + profile.dimensions[1])
            elif profile.type == 'PIPE':
                perimeter = math.pi * profile.dimensions[0]
            else:
                perimeter = 2 * (profile.dimensions[0] + profile.dimensions[1])

            weld_length = perimeter * 0.8  # 80% del perimetro

            # Crear linea de soldadura
            line = member.line
            if center.DistanceTo(line.From) < 1.0:
                weld_start = line.From
                direction = rg.Vector3d(line.To - line.From)
            else:
                weld_start = line.To
                direction = rg.Vector3d(line.From - line.To)

            direction.Unitize()
            weld_end = weld_start + direction * weld_length

            weld_line = rg.Line(weld_start, weld_end)

            # Calcular capacidad
            capacity = self.weld_calc.calculate_fillet_weld(weld_size, weld_length)

            weld = WeldData(
                line=weld_line,
                size=weld_size,
                length=weld_length,
                type='fillet',
                capacity=capacity
            )
            welds.append(weld)

        return welds

    def _create_bolted_connections(self, node_data, connected_members, profile_results):
        """Crea tornillos para conexion atornillada."""
        bolts = []
        center = node_data.point
        bolt_diameter = 20  # mm

        for member in connected_members:
            # Encontrar perfil
            profile = None
            force = 50  # kN estimado

            for pr in profile_results:
                if pr.member_id == member.id:
                    profile = pr.profile
                    break

            if profile is None:
                continue

            # Calcular numero de tornillos
            n_bolts = self.bolt_calc.required_bolts(
                force, bolt_diameter, self.gusset_thickness
            )

            # Posicionar tornillos a lo largo del miembro
            line = member.line
            if center.DistanceTo(line.From) < 1.0:
                start = line.From
                direction = rg.Vector3d(line.To - line.From)
            else:
                start = line.To
                direction = rg.Vector3d(line.From - line.To)

            direction.Unitize()
            spacing = self.bolt_calc.spacing(bolt_diameter)
            edge_dist = self.bolt_calc.edge_distance(bolt_diameter)

            for i in range(n_bolts):
                offset = edge_dist + i * spacing
                bolt_pos = start + direction * offset
                bolts.append(bolt_pos)

        return bolts

    def _create_connection_data(self, node_data, connected_members,
                                 gusset_design, welds, bolts):
        """Crea datos de la conexion."""
        weld_length = sum(w.length for w in welds) if welds else 0
        bolt_count = len(bolts)

        # Calcular capacidad total
        if welds:
            capacity = sum(w.capacity for w in welds)
        elif bolts:
            capacity = bolt_count * self.bolt_calc.shear_capacity(20)
        else:
            capacity = 0

        return ConnectionData(
            node_id=node_data.id,
            type=self.connection_type,
            gusset_plate=gusset_design,
            member_count=len(connected_members),
            weld_length=weld_length,
            bolt_count=bolt_count,
            capacity=capacity,
            utilization=0.5  # Placeholder
        )


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    builder = NodeBuilder(
        connection_type=connection_type if 'connection_type' in dir() else 'welded',
        gusset_thickness=gusset_thickness if 'gusset_thickness' in dir() else 12
    )

    result = builder.build(
        nodes=nodes if 'nodes' in dir() else [],
        node_data=node_data if 'node_data' in dir() else [],
        member_data=member_data if 'member_data' in dir() else [],
        profile_results=profile_results if 'profile_results' in dir() else []
    )

    # Salidas para Grasshopper
    gusset_plates = result.gusset_plates
    welds = result.welds
    bolts = result.bolts
    connection_data = result.connection_data
    total_weld_length = result.total_weld_length
    total_bolt_count = result.total_bolt_count
