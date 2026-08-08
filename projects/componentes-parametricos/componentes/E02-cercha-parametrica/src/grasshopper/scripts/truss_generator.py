"""
Truss Generator - Cercha Parametrica
Genera la geometria de cerchas segun tipologia.

Inputs:
    span (float): Luz de la cercha (mm)
    height (float): Altura en centro (mm)
    slope (float): Pendiente de cuerda superior (grados)
    bay_count (int): Numero de modulos
    truss_type (str): Tipologia de cercha
    base_curve (Curve): Curva base opcional

Outputs:
    top_chord (List[Line]): Segmentos de cuerda superior
    bottom_chord (List[Line]): Segmentos de cuerda inferior
    web_members (List[Line]): Miembros de alma
    nodes (List[Point3d]): Puntos de nodos
    member_data (List[dict]): Datos de cada miembro
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple
from enum import Enum

# Tipos de miembro
class MemberType(Enum):
    TOP_CHORD = "top_chord"
    BOTTOM_CHORD = "bottom_chord"
    DIAGONAL = "diagonal"
    VERTICAL = "vertical"


# Datos del miembro
MemberData = namedtuple('MemberData', [
    'id', 'type', 'line', 'length', 'start_node', 'end_node',
    'angle', 'bay_index'
])

# Datos del nodo
NodeData = namedtuple('NodeData', [
    'id', 'point', 'type', 'connected_members', 'is_support'
])

# Resultado del generador
TrussResult = namedtuple('TrussResult', [
    'top_chord', 'bottom_chord', 'web_members',
    'nodes', 'member_data', 'node_data', 'geometry_stats'
])


class TrussGeometry:
    """Clase base para geometria de cercha."""

    def __init__(self):
        self.tolerance = 0.001

    def create_node_points(self, span, height, slope, bay_count, truss_type):
        """
        Crea los puntos de nodos segun la tipologia.

        Returns:
            tuple: (top_nodes, bottom_nodes)
        """
        raise NotImplementedError("Subclase debe implementar create_node_points")


class TriangularTruss(TrussGeometry):
    """Cercha triangular (cubierta a dos aguas)."""

    def create_node_points(self, span, height, slope, bay_count):
        """Crea nodos para cercha triangular."""
        top_nodes = []
        bottom_nodes = []

        # Calcular altura en el centro si no se especifica
        if height is None or height <= 0:
            height = span * math.tan(math.radians(slope)) / 2

        bay_width = span / bay_count

        for i in range(bay_count + 1):
            x = i * bay_width

            # Nodo inferior (cuerda inferior horizontal)
            bottom_nodes.append(rg.Point3d(x, 0, 0))

            # Nodo superior (cuerda superior inclinada)
            # Forma triangular: sube hasta el centro, luego baja
            if i <= bay_count / 2:
                z = (x / (span / 2)) * height
            else:
                z = ((span - x) / (span / 2)) * height

            top_nodes.append(rg.Point3d(x, 0, z))

        return top_nodes, bottom_nodes


class ParallelTruss(TrussGeometry):
    """Cercha de cuerdas paralelas."""

    def create_node_points(self, span, height, slope, bay_count):
        """Crea nodos para cercha paralela."""
        top_nodes = []
        bottom_nodes = []

        # Si hay pendiente, aplicarla uniformemente
        if slope > 0:
            rise = span * math.tan(math.radians(slope))
        else:
            rise = 0

        bay_width = span / bay_count

        for i in range(bay_count + 1):
            x = i * bay_width
            z_offset = (x / span) * rise if rise > 0 else 0

            # Nodo inferior
            bottom_nodes.append(rg.Point3d(x, 0, z_offset))

            # Nodo superior (paralelo a altura constante)
            top_nodes.append(rg.Point3d(x, 0, height + z_offset))

        return top_nodes, bottom_nodes


class BowstringTruss(TrussGeometry):
    """Cercha con cuerda superior curva."""

    def create_node_points(self, span, height, slope, bay_count):
        """Crea nodos para cercha bowstring."""
        top_nodes = []
        bottom_nodes = []

        bay_width = span / bay_count

        for i in range(bay_count + 1):
            x = i * bay_width

            # Nodo inferior (cuerda inferior recta)
            bottom_nodes.append(rg.Point3d(x, 0, 0))

            # Nodo superior (arco parabolico)
            # Parabola: z = 4h * x * (L-x) / L^2
            z = 4 * height * x * (span - x) / (span ** 2)
            top_nodes.append(rg.Point3d(x, 0, z))

        return top_nodes, bottom_nodes


class CrescentTruss(TrussGeometry):
    """Cercha con ambas cuerdas curvas."""

    def create_node_points(self, span, height, slope, bay_count):
        """Crea nodos para cercha crescent."""
        top_nodes = []
        bottom_nodes = []

        bay_width = span / bay_count
        bottom_height = height * 0.3  # Curvatura inferior = 30% de altura

        for i in range(bay_count + 1):
            x = i * bay_width

            # Parabola superior
            z_top = 4 * height * x * (span - x) / (span ** 2)

            # Parabola inferior (invertida, mas suave)
            z_bottom = -4 * bottom_height * x * (span - x) / (span ** 2)

            bottom_nodes.append(rg.Point3d(x, 0, z_bottom))
            top_nodes.append(rg.Point3d(x, 0, z_top))

        return top_nodes, bottom_nodes


class TrussGenerator:
    """Generador principal de cerchas."""

    # Mapeo de tipologias a clases de geometria
    GEOMETRY_CLASSES = {
        'fink': TriangularTruss,
        'howe': TriangularTruss,
        'pratt': TriangularTruss,
        'warren': TriangularTruss,
        'warren_vertical': TriangularTruss,
        'scissors': TriangularTruss,
        'fan': TriangularTruss,
        'parallel_pratt': ParallelTruss,
        'parallel_warren': ParallelTruss,
        'vierendeel': ParallelTruss,
        'bowstring': BowstringTruss,
        'crescent': CrescentTruss,
        'lenticular': CrescentTruss,
    }

    def __init__(self):
        self.tolerance = 0.001
        self.member_id_counter = 0
        self.node_id_counter = 0

    def generate(self, span, height=None, slope=15, bay_count=8,
                 truss_type='pratt', base_curve=None):
        """
        Genera la cercha completa.

        Args:
            span: Luz de la cercha (mm)
            height: Altura en centro (mm)
            slope: Pendiente (grados)
            bay_count: Numero de modulos
            truss_type: Tipologia de cercha
            base_curve: Curva base opcional

        Returns:
            TrussResult
        """
        # Validar parametros
        span = float(span)
        bay_count = max(4, int(bay_count))
        slope = max(0, min(45, float(slope)))

        # Calcular altura si no se especifica
        if height is None or height <= 0:
            height = self._calculate_optimal_height(span, truss_type)

        height = float(height)

        # Obtener clase de geometria
        geometry_class = self.GEOMETRY_CLASSES.get(truss_type, TriangularTruss)
        geometry = geometry_class()

        # Crear nodos
        top_nodes, bottom_nodes = geometry.create_node_points(
            span, height, slope, bay_count
        )

        # Transformar si hay curva base
        if base_curve is not None:
            top_nodes, bottom_nodes = self._transform_to_curve(
                top_nodes, bottom_nodes, base_curve
            )

        # Crear miembros de cuerda
        top_chord = self._create_chord_members(
            top_nodes, MemberType.TOP_CHORD
        )
        bottom_chord = self._create_chord_members(
            bottom_nodes, MemberType.BOTTOM_CHORD
        )

        # Crear miembros de alma segun tipologia
        web_members = self._create_web_members(
            top_nodes, bottom_nodes, truss_type, bay_count
        )

        # Crear datos de nodos
        all_nodes = self._create_all_nodes(top_nodes, bottom_nodes)
        node_data = self._create_node_data(all_nodes, top_chord + bottom_chord + web_members)

        # Calcular estadisticas
        all_members = top_chord + bottom_chord + web_members
        stats = self._calculate_stats(all_members, span, height)

        return TrussResult(
            top_chord=[m.line for m in top_chord],
            bottom_chord=[m.line for m in bottom_chord],
            web_members=[m.line for m in web_members],
            nodes=all_nodes,
            member_data=all_members,
            node_data=node_data,
            geometry_stats=stats
        )

    def _calculate_optimal_height(self, span, truss_type):
        """Calcula altura optima segun tipologia."""
        ratios = {
            'fink': 0.20,
            'howe': 0.15,
            'pratt': 0.12,
            'warren': 0.10,
            'warren_vertical': 0.10,
            'scissors': 0.25,
            'fan': 0.18,
            'parallel_pratt': 0.08,
            'parallel_warren': 0.07,
            'vierendeel': 0.10,
            'bowstring': 0.12,
            'crescent': 0.15,
            'lenticular': 0.08,
        }
        ratio = ratios.get(truss_type, 0.10)
        return span * ratio

    def _create_chord_members(self, nodes, member_type):
        """Crea miembros de cuerda (superior o inferior)."""
        members = []

        for i in range(len(nodes) - 1):
            line = rg.Line(nodes[i], nodes[i + 1])
            length = line.Length

            # Calcular angulo
            dx = nodes[i + 1].X - nodes[i].X
            dz = nodes[i + 1].Z - nodes[i].Z
            angle = math.degrees(math.atan2(dz, dx))

            member = MemberData(
                id=self._get_next_member_id(),
                type=member_type,
                line=line,
                length=length,
                start_node=i,
                end_node=i + 1,
                angle=angle,
                bay_index=i
            )
            members.append(member)

        return members

    def _create_web_members(self, top_nodes, bottom_nodes, truss_type, bay_count):
        """Crea miembros de alma segun tipologia."""
        web_members = []

        if truss_type == 'warren':
            web_members = self._create_warren_web(top_nodes, bottom_nodes, False)

        elif truss_type == 'warren_vertical':
            web_members = self._create_warren_web(top_nodes, bottom_nodes, True)

        elif truss_type == 'pratt':
            web_members = self._create_pratt_web(top_nodes, bottom_nodes, 'inward')

        elif truss_type == 'howe':
            web_members = self._create_pratt_web(top_nodes, bottom_nodes, 'outward')

        elif truss_type == 'fink':
            web_members = self._create_fink_web(top_nodes, bottom_nodes)

        elif truss_type == 'fan':
            web_members = self._create_fan_web(top_nodes, bottom_nodes)

        elif truss_type == 'scissors':
            web_members = self._create_scissors_web(top_nodes, bottom_nodes)

        elif truss_type in ['parallel_pratt', 'parallel_warren']:
            web_members = self._create_parallel_web(
                top_nodes, bottom_nodes,
                'warren' if 'warren' in truss_type else 'pratt'
            )

        elif truss_type == 'vierendeel':
            web_members = self._create_vierendeel_web(top_nodes, bottom_nodes)

        elif truss_type in ['bowstring', 'crescent', 'lenticular']:
            web_members = self._create_curved_web(top_nodes, bottom_nodes)

        return web_members

    def _create_warren_web(self, top_nodes, bottom_nodes, with_verticals):
        """Crea alma tipo Warren."""
        members = []
        n = len(top_nodes)

        for i in range(n - 1):
            # Diagonal alternada
            if i % 2 == 0:
                # Diagonal de bottom[i] a top[i+1]
                line = rg.Line(bottom_nodes[i], top_nodes[i + 1])
            else:
                # Diagonal de top[i] a bottom[i+1]
                line = rg.Line(top_nodes[i], bottom_nodes[i + 1])

            member = self._create_member(
                line, MemberType.DIAGONAL,
                i, i + 1, i
            )
            members.append(member)

        # Agregar verticales si se requieren
        if with_verticals:
            for i in range(1, n - 1):
                line = rg.Line(bottom_nodes[i], top_nodes[i])
                member = self._create_member(
                    line, MemberType.VERTICAL,
                    i, i, i
                )
                members.append(member)

        return members

    def _create_pratt_web(self, top_nodes, bottom_nodes, direction):
        """
        Crea alma tipo Pratt o Howe.

        direction: 'inward' para Pratt, 'outward' para Howe
        """
        members = []
        n = len(top_nodes)
        mid = n // 2

        # Verticales
        for i in range(1, n - 1):
            line = rg.Line(bottom_nodes[i], top_nodes[i])
            member = self._create_member(
                line, MemberType.VERTICAL,
                i, i, i
            )
            members.append(member)

        # Diagonales
        for i in range(n - 1):
            if direction == 'inward':
                # Pratt: diagonales hacia el centro
                if i < mid:
                    line = rg.Line(bottom_nodes[i], top_nodes[i + 1])
                else:
                    line = rg.Line(bottom_nodes[i + 1], top_nodes[i])
            else:
                # Howe: diagonales hacia afuera
                if i < mid:
                    line = rg.Line(top_nodes[i], bottom_nodes[i + 1])
                else:
                    line = rg.Line(top_nodes[i + 1], bottom_nodes[i])

            member = self._create_member(
                line, MemberType.DIAGONAL,
                i, i + 1, i
            )
            members.append(member)

        return members

    def _create_fink_web(self, top_nodes, bottom_nodes):
        """Crea alma tipo Fink (patron W)."""
        members = []
        n = len(top_nodes)
        mid = n // 2

        # Vertical central
        line = rg.Line(bottom_nodes[mid], top_nodes[mid])
        members.append(self._create_member(line, MemberType.VERTICAL, mid, mid, mid))

        # Diagonales en W
        # Lado izquierdo
        for i in range(mid):
            if i % 2 == 0:
                line = rg.Line(bottom_nodes[i], top_nodes[i + 1])
            else:
                line = rg.Line(top_nodes[i], bottom_nodes[i + 1])
            members.append(self._create_member(line, MemberType.DIAGONAL, i, i+1, i))

        # Lado derecho (espejo)
        for i in range(mid, n - 1):
            if (n - 1 - i) % 2 == 0:
                line = rg.Line(bottom_nodes[i + 1], top_nodes[i])
            else:
                line = rg.Line(top_nodes[i + 1], bottom_nodes[i])
            members.append(self._create_member(line, MemberType.DIAGONAL, i, i+1, i))

        return members

    def _create_fan_web(self, top_nodes, bottom_nodes):
        """Crea alma tipo Fan (radial desde apoyos)."""
        members = []
        n = len(top_nodes)

        # Desde apoyo izquierdo
        for i in range(1, n // 2 + 1):
            line = rg.Line(bottom_nodes[0], top_nodes[i])
            members.append(self._create_member(line, MemberType.DIAGONAL, 0, i, i))

        # Desde apoyo derecho
        for i in range(n // 2, n - 1):
            line = rg.Line(bottom_nodes[n - 1], top_nodes[i])
            members.append(self._create_member(line, MemberType.DIAGONAL, n-1, i, i))

        # Verticales intermedios
        for i in range(1, n - 1):
            line = rg.Line(bottom_nodes[i], top_nodes[i])
            members.append(self._create_member(line, MemberType.VERTICAL, i, i, i))

        return members

    def _create_scissors_web(self, top_nodes, bottom_nodes):
        """Crea alma tipo Scissors (cuerdas cruzadas)."""
        members = []
        n = len(top_nodes)
        mid = n // 2

        # Las cuerdas interiores se cruzan
        # Crear diagonales cruzadas desde los cuartos
        quarter = n // 4

        # Diagonal principal izquierda-derecha
        line1 = rg.Line(bottom_nodes[quarter], top_nodes[n - quarter - 1])
        members.append(self._create_member(line1, MemberType.DIAGONAL, quarter, n-quarter-1, 0))

        # Diagonal principal derecha-izquierda
        line2 = rg.Line(bottom_nodes[n - quarter - 1], top_nodes[quarter])
        members.append(self._create_member(line2, MemberType.DIAGONAL, n-quarter-1, quarter, 1))

        # Verticales en extremos
        for i in [0, n - 1]:
            line = rg.Line(bottom_nodes[i], top_nodes[i])
            members.append(self._create_member(line, MemberType.VERTICAL, i, i, i))

        # Diagonales adicionales
        for i in range(1, mid):
            line = rg.Line(bottom_nodes[i], top_nodes[i + 1])
            members.append(self._create_member(line, MemberType.DIAGONAL, i, i+1, i))

        for i in range(mid, n - 1):
            line = rg.Line(bottom_nodes[i + 1], top_nodes[i])
            members.append(self._create_member(line, MemberType.DIAGONAL, i+1, i, i))

        return members

    def _create_parallel_web(self, top_nodes, bottom_nodes, style):
        """Crea alma para cerchas paralelas."""
        if style == 'warren':
            return self._create_warren_web(top_nodes, bottom_nodes, True)
        else:
            return self._create_pratt_web(top_nodes, bottom_nodes, 'inward')

    def _create_vierendeel_web(self, top_nodes, bottom_nodes):
        """Crea alma tipo Vierendeel (solo verticales, sin diagonales)."""
        members = []
        n = len(top_nodes)

        for i in range(n):
            line = rg.Line(bottom_nodes[i], top_nodes[i])
            members.append(self._create_member(line, MemberType.VERTICAL, i, i, i))

        return members

    def _create_curved_web(self, top_nodes, bottom_nodes):
        """Crea alma para cerchas curvas (bowstring, crescent)."""
        # Usar patron Warren con verticales
        return self._create_warren_web(top_nodes, bottom_nodes, True)

    def _create_member(self, line, member_type, start_node, end_node, bay_index):
        """Crea un MemberData."""
        dx = line.To.X - line.From.X
        dz = line.To.Z - line.From.Z
        angle = math.degrees(math.atan2(dz, dx))

        return MemberData(
            id=self._get_next_member_id(),
            type=member_type,
            line=line,
            length=line.Length,
            start_node=start_node,
            end_node=end_node,
            angle=abs(angle),
            bay_index=bay_index
        )

    def _create_all_nodes(self, top_nodes, bottom_nodes):
        """Combina todos los nodos unicos."""
        all_nodes = []
        all_nodes.extend(bottom_nodes)
        all_nodes.extend(top_nodes)
        return all_nodes

    def _create_node_data(self, nodes, members):
        """Crea datos de cada nodo."""
        node_data = []

        for i, node in enumerate(nodes):
            # Encontrar miembros conectados
            connected = []
            for m in members:
                if m.start_node == i or m.end_node == i:
                    connected.append(m.id)

            # Determinar tipo de nodo
            is_bottom = i < len(nodes) // 2
            is_support = is_bottom and (i == 0 or i == len(nodes) // 2 - 1)

            if is_support:
                node_type = 'support'
            elif is_bottom:
                node_type = 'bottom'
            else:
                node_type = 'top'

            data = NodeData(
                id=self._get_next_node_id(),
                point=node,
                type=node_type,
                connected_members=connected,
                is_support=is_support
            )
            node_data.append(data)

        return node_data

    def _transform_to_curve(self, top_nodes, bottom_nodes, base_curve):
        """Transforma los nodos a una curva base."""
        transformed_top = []
        transformed_bottom = []

        # Obtener longitud total
        span = top_nodes[-1].X - top_nodes[0].X
        curve_length = base_curve.GetLength()

        for i, (top, bottom) in enumerate(zip(top_nodes, bottom_nodes)):
            # Parametro normalizado
            t = top.X / span
            # Punto en la curva
            curve_param = base_curve.Domain.T0 + t * (base_curve.Domain.T1 - base_curve.Domain.T0)
            curve_point = base_curve.PointAt(curve_param)

            # Obtener frame
            success, plane = base_curve.PerpendicularFrameAt(curve_param)
            if not success:
                plane = rg.Plane.WorldXY
                plane.Origin = curve_point

            # Transformar puntos
            offset_top = rg.Point3d(0, 0, top.Z)
            offset_bottom = rg.Point3d(0, 0, bottom.Z)

            transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)

            new_top = rg.Point3d(offset_top)
            new_top.Transform(transform)
            new_top += rg.Vector3d(curve_point)

            new_bottom = rg.Point3d(offset_bottom)
            new_bottom.Transform(transform)
            new_bottom += rg.Vector3d(curve_point)

            transformed_top.append(new_top)
            transformed_bottom.append(new_bottom)

        return transformed_top, transformed_bottom

    def _calculate_stats(self, members, span, height):
        """Calcula estadisticas de la geometria."""
        total_length = sum(m.length for m in members)

        top_chord_length = sum(m.length for m in members if m.type == MemberType.TOP_CHORD)
        bottom_chord_length = sum(m.length for m in members if m.type == MemberType.BOTTOM_CHORD)
        web_length = sum(m.length for m in members if m.type in [MemberType.DIAGONAL, MemberType.VERTICAL])

        diagonal_count = sum(1 for m in members if m.type == MemberType.DIAGONAL)
        vertical_count = sum(1 for m in members if m.type == MemberType.VERTICAL)

        # Angulos de diagonales
        diagonal_angles = [m.angle for m in members if m.type == MemberType.DIAGONAL]
        avg_angle = sum(diagonal_angles) / len(diagonal_angles) if diagonal_angles else 0

        return {
            'span': span,
            'height': height,
            'height_ratio': height / span,
            'total_length': total_length,
            'top_chord_length': top_chord_length,
            'bottom_chord_length': bottom_chord_length,
            'web_length': web_length,
            'member_count': len(members),
            'diagonal_count': diagonal_count,
            'vertical_count': vertical_count,
            'avg_diagonal_angle': avg_angle
        }

    def _get_next_member_id(self):
        """Obtiene siguiente ID de miembro."""
        self.member_id_counter += 1
        return f"M{self.member_id_counter:03d}"

    def _get_next_node_id(self):
        """Obtiene siguiente ID de nodo."""
        self.node_id_counter += 1
        return f"N{self.node_id_counter:03d}"


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    generator = TrussGenerator()

    result = generator.generate(
        span=span if 'span' in dir() else 12000,
        height=height if 'height' in dir() else None,
        slope=slope if 'slope' in dir() else 15,
        bay_count=bay_count if 'bay_count' in dir() else 8,
        truss_type=truss_type if 'truss_type' in dir() else 'pratt',
        base_curve=base_curve if 'base_curve' in dir() else None
    )

    # Salidas para Grasshopper
    top_chord = result.top_chord
    bottom_chord = result.bottom_chord
    web_members = result.web_members
    nodes = result.nodes
    member_data = result.member_data
    geometry_stats = result.geometry_stats
