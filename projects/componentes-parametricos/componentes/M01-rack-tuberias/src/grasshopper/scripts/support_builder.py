"""
Support Builder - Rack de Tuberias Parametrico
Genera soportes de tuberia, guias, anclajes y bandejas de cables.

Inputs:
    rack_data (RackData): Datos de la estructura del rack
    pipe_schedule (List[dict]): Lista de tuberias {size, count, service}
    support_type (str): Tipo de soporte por defecto
    support_spacing (float): Espaciamiento de soportes (mm)
    include_tray (bool): Incluir bandeja de cables
    tray_config (dict): Configuracion de bandeja

Outputs:
    supports (List[Brep]): Geometria de soportes
    shoes (List[Brep]): Zapatas de tuberia
    guides (List[Brep]): Guias
    anchors (List[Brep]): Anclajes
    cable_tray (List[Brep]): Bandeja de cables
    support_data (dict): Datos de soportes
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de soporte
SupportData = namedtuple('SupportData', [
    'id', 'type', 'pipe_size', 'position', 'height',
    'load_capacity', 'brep'
])

# Resultado del constructor
SupportResult = namedtuple('SupportResult', [
    'shoes', 'guides', 'anchors', 'hangers',
    'cable_tray', 'support_list', 'total_count',
    'total_weight', 'summary'
])

# Dimensiones de soportes por tamano de tuberia (NPS en pulgadas)
SUPPORT_DIMENSIONS = {
    2: {'shoe_width': 100, 'shoe_height': 75, 'shoe_length': 150, 'bolt_size': 12},
    3: {'shoe_width': 125, 'shoe_height': 100, 'shoe_length': 175, 'bolt_size': 16},
    4: {'shoe_width': 150, 'shoe_height': 100, 'shoe_length': 200, 'bolt_size': 16},
    6: {'shoe_width': 200, 'shoe_height': 125, 'shoe_length': 250, 'bolt_size': 20},
    8: {'shoe_width': 250, 'shoe_height': 150, 'shoe_length': 300, 'bolt_size': 20},
    10: {'shoe_width': 300, 'shoe_height': 175, 'shoe_length': 350, 'bolt_size': 22},
    12: {'shoe_width': 350, 'shoe_height': 200, 'shoe_length': 400, 'bolt_size': 24},
    14: {'shoe_width': 400, 'shoe_height': 225, 'shoe_length': 450, 'bolt_size': 24},
    16: {'shoe_width': 450, 'shoe_height': 250, 'shoe_length': 500, 'bolt_size': 27},
    18: {'shoe_width': 500, 'shoe_height': 275, 'shoe_length': 550, 'bolt_size': 27},
    20: {'shoe_width': 550, 'shoe_height': 300, 'shoe_length': 600, 'bolt_size': 30},
    24: {'shoe_width': 650, 'shoe_height': 350, 'shoe_length': 700, 'bolt_size': 30},
}

# Espaciamiento de soportes por servicio
SUPPORT_SPACING = {
    'water': {2: 2400, 3: 3000, 4: 3600, 6: 4200, 8: 4800, 10: 5200, 12: 5800},
    'steam': {2: 2700, 3: 3300, 4: 3900, 6: 4800, 8: 5400, 10: 6000, 12: 6600},
    'gas': {2: 3000, 3: 3600, 4: 4200, 6: 5100, 8: 5800, 10: 6400, 12: 7000},
    'oil': {2: 2400, 3: 3000, 4: 3600, 6: 4200, 8: 4800, 10: 5200, 12: 5800},
}


class PipeShoeBuilder:
    """Construye zapatas (shoes) para tuberias."""

    def __init__(self, material='carbon_steel'):
        self.material = material
        self.density = 7850  # kg/m3

    def get_dimensions(self, pipe_size):
        """Obtiene dimensiones de zapata para tamano de tuberia."""
        # Buscar tamano mas cercano
        sizes = sorted(SUPPORT_DIMENSIONS.keys())
        for s in sizes:
            if pipe_size <= s:
                return SUPPORT_DIMENSIONS[s]
        return SUPPORT_DIMENSIONS[max(sizes)]

    def create_shoe(self, position, pipe_size, insulation_gap=50,
                    rotation_angle=0):
        """
        Crea una zapata de tuberia.

        Args:
            position: Punto de ubicacion
            pipe_size: Tamano de tuberia (NPS)
            insulation_gap: Gap para aislamiento (mm)
            rotation_angle: Angulo de rotacion (grados)

        Returns:
            Brep: Geometria de la zapata
        """
        dims = self.get_dimensions(pipe_size)

        # Dimensiones
        width = dims['shoe_width']
        height = dims['shoe_height']
        length = dims['shoe_length']
        plate_thickness = 12  # mm

        # Crear perfil de zapata (vista lateral)
        # Base + verticales + soporte curvo
        profile_points = [
            rg.Point3d(-length/2, 0, 0),
            rg.Point3d(length/2, 0, 0),
            rg.Point3d(length/2, 0, plate_thickness),
            rg.Point3d(-length/2, 0, plate_thickness),
            rg.Point3d(-length/2, 0, 0),
        ]

        # Placa base
        base_rect = rg.Rectangle3d(
            rg.Plane(position, rg.Vector3d.ZAxis),
            rg.Interval(-length/2, length/2),
            rg.Interval(-width/2, width/2)
        )

        base_extrusion = rg.Extrusion.Create(
            base_rect.ToNurbsCurve(),
            plate_thickness,
            True
        )

        breps = []
        if base_extrusion:
            breps.append(base_extrusion.ToBrep())

        # Verticales (2 placas)
        vertical_height = height - plate_thickness
        for y_offset in [-width/4, width/4]:
            vert_plane = rg.Plane(
                rg.Point3d(position.X, position.Y + y_offset, position.Z + plate_thickness),
                rg.Vector3d.YAxis
            )
            vert_rect = rg.Rectangle3d(
                vert_plane,
                rg.Interval(-length/4, length/4),
                rg.Interval(0, vertical_height)
            )

            vert_ext = rg.Extrusion.Create(
                vert_rect.ToNurbsCurve(),
                plate_thickness,
                True
            )

            if vert_ext:
                breps.append(vert_ext.ToBrep())

        # Placa superior (soporte de tuberia)
        top_plane = rg.Plane(
            rg.Point3d(position.X, position.Y, position.Z + height),
            rg.Vector3d.ZAxis
        )
        top_rect = rg.Rectangle3d(
            top_plane,
            rg.Interval(-length/3, length/3),
            rg.Interval(-width/2 + insulation_gap, width/2 - insulation_gap)
        )

        top_ext = rg.Extrusion.Create(
            top_rect.ToNurbsCurve(),
            plate_thickness,
            True
        )

        if top_ext:
            breps.append(top_ext.ToBrep())

        # Unir breps
        if len(breps) > 1:
            joined = rg.Brep.JoinBreps(breps, 0.01)
            if joined and len(joined) > 0:
                return joined[0]

        return breps[0] if breps else None

    def calculate_weight(self, pipe_size):
        """Calcula peso de la zapata."""
        dims = self.get_dimensions(pipe_size)
        # Estimacion basada en volumen aproximado
        volume = (dims['shoe_width'] * dims['shoe_length'] * 12 +
                  2 * dims['shoe_length']/2 * dims['shoe_height'] * 12 +
                  dims['shoe_length']/1.5 * dims['shoe_width']/2 * 12) / 1e9
        return volume * self.density


class PipeGuideBuilder:
    """Construye guias para tuberias."""

    def __init__(self, material='carbon_steel'):
        self.material = material

    def create_guide(self, position, pipe_size, clearance=3, guide_height=150):
        """
        Crea una guia de tuberia.

        Args:
            position: Punto de ubicacion
            pipe_size: Tamano de tuberia (NPS)
            clearance: Holgura lateral (mm)
            guide_height: Altura de la guia (mm)

        Returns:
            Brep: Geometria de la guia
        """
        # Diametro exterior de tuberia (aproximado)
        pipe_od = pipe_size * 25.4 + 10  # mm (aproximacion)

        # Dimensiones de guia
        guide_width = pipe_od + 2 * clearance + 50
        guide_length = 200
        plate_thickness = 10

        breps = []

        # Base de la guia
        base_plane = rg.Plane(position, rg.Vector3d.ZAxis)
        base_rect = rg.Rectangle3d(
            base_plane,
            rg.Interval(-guide_length/2, guide_length/2),
            rg.Interval(-guide_width/2, guide_width/2)
        )

        base_ext = rg.Extrusion.Create(
            base_rect.ToNurbsCurve(),
            plate_thickness,
            True
        )

        if base_ext:
            breps.append(base_ext.ToBrep())

        # Placas laterales (guias)
        for y_sign in [-1, 1]:
            y_offset = y_sign * (pipe_od/2 + clearance + plate_thickness/2)

            side_plane = rg.Plane(
                rg.Point3d(position.X, position.Y + y_offset, position.Z + plate_thickness),
                rg.Vector3d.YAxis
            )

            side_rect = rg.Rectangle3d(
                side_plane,
                rg.Interval(-guide_length/2, guide_length/2),
                rg.Interval(0, guide_height)
            )

            side_ext = rg.Extrusion.Create(
                side_rect.ToNurbsCurve(),
                plate_thickness,
                True
            )

            if side_ext:
                breps.append(side_ext.ToBrep())

        # Unir
        if len(breps) > 1:
            joined = rg.Brep.JoinBreps(breps, 0.01)
            if joined and len(joined) > 0:
                return joined[0]

        return breps[0] if breps else None


class PipeAnchorBuilder:
    """Construye anclajes para tuberias."""

    def __init__(self, material='carbon_steel'):
        self.material = material

    def create_anchor(self, position, pipe_size, anchor_height=200):
        """
        Crea un anclaje de tuberia.

        Args:
            position: Punto de ubicacion
            pipe_size: Tamano de tuberia (NPS)
            anchor_height: Altura del anclaje (mm)

        Returns:
            Brep: Geometria del anclaje
        """
        pipe_od = pipe_size * 25.4 + 10
        anchor_width = pipe_od + 100
        anchor_length = 300
        plate_thickness = 16

        breps = []

        # Base robusta
        base_plane = rg.Plane(position, rg.Vector3d.ZAxis)
        base_rect = rg.Rectangle3d(
            base_plane,
            rg.Interval(-anchor_length/2, anchor_length/2),
            rg.Interval(-anchor_width/2, anchor_width/2)
        )

        base_ext = rg.Extrusion.Create(
            base_rect.ToNurbsCurve(),
            plate_thickness,
            True
        )

        if base_ext:
            breps.append(base_ext.ToBrep())

        # Placas de restriccion (4 lados)
        for angle in [0, 90, 180, 270]:
            angle_rad = math.radians(angle)

            if angle in [0, 180]:
                offset = anchor_length/2 - plate_thickness
                rect_width = anchor_width - 20
            else:
                offset = anchor_width/2 - plate_thickness
                rect_width = anchor_length - 20

            x_off = offset * math.cos(angle_rad)
            y_off = offset * math.sin(angle_rad)

            stop_plane = rg.Plane(
                rg.Point3d(position.X + x_off, position.Y + y_off, position.Z + plate_thickness),
                rg.Vector3d(math.cos(angle_rad), math.sin(angle_rad), 0)
            )

            stop_rect = rg.Rectangle3d(
                stop_plane,
                rg.Interval(-rect_width/2, rect_width/2),
                rg.Interval(0, anchor_height)
            )

            stop_ext = rg.Extrusion.Create(
                stop_rect.ToNurbsCurve(),
                plate_thickness,
                True
            )

            if stop_ext:
                breps.append(stop_ext.ToBrep())

        # Unir
        if len(breps) > 1:
            joined = rg.Brep.JoinBreps(breps, 0.01)
            if joined and len(joined) > 0:
                return joined[0]

        return breps[0] if breps else None


class CableTrayBuilder:
    """Construye bandejas de cables."""

    TRAY_TYPES = {
        'ladder': {'rung_spacing': 230, 'side_height': 100, 'rung_width': 25},
        'solid': {'side_height': 75, 'bottom_thickness': 2},
        'mesh': {'wire_diameter': 4, 'mesh_size': 50, 'side_height': 75},
        'channel': {'side_height': 50, 'bottom_thickness': 1.5},
    }

    def __init__(self, tray_type='ladder'):
        self.tray_type = tray_type
        self.config = self.TRAY_TYPES.get(tray_type, self.TRAY_TYPES['ladder'])

    def create_tray_segment(self, start_point, end_point, width=600, height=100):
        """
        Crea un segmento de bandeja.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            width: Ancho de la bandeja (mm)
            height: Altura lateral (mm)

        Returns:
            Brep: Geometria de la bandeja
        """
        length = start_point.DistanceTo(end_point)
        direction = end_point - start_point
        direction.Unitize()

        breps = []

        if self.tray_type == 'ladder':
            # Bandeja tipo escalera
            side_thickness = 3
            rung_height = 25
            rung_spacing = self.config['rung_spacing']

            # Laterales
            for y_offset in [-width/2, width/2 - side_thickness]:
                side_plane = rg.Plane(
                    rg.Point3d(start_point.X, start_point.Y + y_offset, start_point.Z),
                    direction
                )

                # Perfil C del lateral
                side_profile = rg.Rectangle3d(
                    rg.Plane.WorldXY,
                    rg.Interval(0, side_thickness),
                    rg.Interval(0, height)
                )

                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, side_plane)
                side_curve = side_profile.ToNurbsCurve()
                side_curve.Transform(xform)

                side_ext = rg.Extrusion.Create(side_curve, length, True)
                if side_ext:
                    breps.append(side_ext.ToBrep())

            # Travesanos
            rung_count = int(length / rung_spacing) + 1
            for i in range(rung_count):
                x_offset = i * rung_spacing
                if x_offset > length:
                    break

                rung_start = rg.Point3d(
                    start_point.X + direction.X * x_offset,
                    start_point.Y - width/2 + side_thickness,
                    start_point.Z
                )
                rung_end = rg.Point3d(
                    start_point.X + direction.X * x_offset,
                    start_point.Y + width/2 - side_thickness,
                    start_point.Z
                )

                rung_line = rg.Line(rung_start, rung_end)
                rung_circle = rg.Circle(
                    rg.Plane(rung_start, rung_end - rung_start),
                    rung_height / 2
                )

                pipe = rg.Brep.CreatePipe(
                    rung_line.ToNurbsCurve(),
                    rung_height / 2,
                    False,
                    rg.PipeCapMode.Flat,
                    True,
                    0.01,
                    0.01
                )

                if pipe:
                    breps.extend(pipe)

        elif self.tray_type == 'solid':
            # Bandeja solida
            bottom_thickness = self.config['bottom_thickness']

            # Fondo
            bottom_plane = rg.Plane(start_point, direction)
            bottom_rect = rg.Rectangle3d(
                bottom_plane,
                rg.Interval(-width/2, width/2),
                rg.Interval(0, length)
            )

            # Rotar para alinear con direccion
            # Simplificado: crear caja
            box = rg.Box(
                rg.Plane(start_point, rg.Vector3d.ZAxis),
                rg.Interval(-width/2, width/2),
                rg.Interval(0, length),
                rg.Interval(0, bottom_thickness)
            )

            breps.append(box.ToBrep())

            # Laterales
            for y_offset in [-width/2, width/2]:
                side_box = rg.Box(
                    rg.Plane(rg.Point3d(start_point.X, start_point.Y + y_offset, start_point.Z), rg.Vector3d.ZAxis),
                    rg.Interval(-2, 2),
                    rg.Interval(0, length),
                    rg.Interval(0, height)
                )
                breps.append(side_box.ToBrep())

        # Unir
        if len(breps) > 1:
            joined = rg.Brep.JoinBreps(breps, 0.01)
            if joined and len(joined) > 0:
                return joined[0]

        return breps[0] if breps else None


class SupportBuilder:
    """Constructor principal de soportes."""

    def __init__(self, default_support_type='shoe'):
        self.default_type = default_support_type
        self.shoe_builder = PipeShoeBuilder()
        self.guide_builder = PipeGuideBuilder()
        self.anchor_builder = PipeAnchorBuilder()
        self.tray_builder = CableTrayBuilder()

    def build(self, rack_data, pipe_schedule, support_spacing=3000,
              insulation_gap=50, include_tray=True, tray_width=600,
              tray_tier=1):
        """
        Construye todos los soportes para el rack.

        Args:
            rack_data: Datos del rack
            pipe_schedule: Lista de tuberias [{size, count, service, tier}]
            support_spacing: Espaciamiento de soportes (mm)
            insulation_gap: Gap para aislamiento (mm)
            include_tray: Incluir bandeja de cables
            tray_width: Ancho de bandeja (mm)
            tray_tier: Nivel de la bandeja

        Returns:
            SupportResult
        """
        all_shoes = []
        all_guides = []
        all_anchors = []
        all_hangers = []
        all_tray = []
        support_list = []

        summary = rack_data.summary
        total_length = summary['total_length']
        bay_spacing = summary['bay_spacing']
        width = summary['width']
        tier_heights = summary['tier_heights']

        total_weight = 0

        # Generar soportes para cada linea de tuberia
        for pipe_info in pipe_schedule:
            pipe_size = pipe_info.get('size', 6)
            pipe_count = pipe_info.get('count', 1)
            service = pipe_info.get('service', 'water')
            tier = pipe_info.get('tier', 0)

            if tier >= len(tier_heights):
                tier = len(tier_heights) - 1

            tier_height = tier_heights[tier]

            # Calcular espaciamiento optimo
            spacing_table = SUPPORT_SPACING.get(service, SUPPORT_SPACING['water'])
            optimal_spacing = spacing_table.get(pipe_size, support_spacing)
            actual_spacing = min(optimal_spacing, support_spacing, bay_spacing)

            # Posiciones de soportes
            support_count = int(total_length / actual_spacing) + 1

            for i in range(support_count):
                x_pos = i * actual_spacing
                if x_pos > total_length:
                    break

                # Distribuir tuberias en el nivel
                for j in range(pipe_count):
                    # Offset en Y para cada tuberia
                    y_offset = -width/2 + 200 + j * 150  # 150mm entre tuberias

                    position = rg.Point3d(x_pos, y_offset, tier_height)

                    # Determinar tipo de soporte
                    if i == 0 or i == support_count - 1:
                        # Anclajes en extremos
                        brep = self.anchor_builder.create_anchor(
                            position, pipe_size
                        )
                        if brep:
                            all_anchors.append(brep)
                            support_list.append(SupportData(
                                id=f"ANC-{len(support_list)+1:03d}",
                                type='anchor',
                                pipe_size=pipe_size,
                                position=position,
                                height=200,
                                load_capacity=self._get_load_capacity(pipe_size, 'anchor'),
                                brep=brep
                            ))

                    elif i % 4 == 0:
                        # Guias cada 4 soportes
                        brep = self.guide_builder.create_guide(
                            position, pipe_size
                        )
                        if brep:
                            all_guides.append(brep)
                            support_list.append(SupportData(
                                id=f"GDE-{len(support_list)+1:03d}",
                                type='guide',
                                pipe_size=pipe_size,
                                position=position,
                                height=150,
                                load_capacity=self._get_load_capacity(pipe_size, 'guide'),
                                brep=brep
                            ))

                    else:
                        # Zapatas en el resto
                        brep = self.shoe_builder.create_shoe(
                            position, pipe_size, insulation_gap
                        )
                        if brep:
                            all_shoes.append(brep)
                            total_weight += self.shoe_builder.calculate_weight(pipe_size)
                            support_list.append(SupportData(
                                id=f"SHO-{len(support_list)+1:03d}",
                                type='shoe',
                                pipe_size=pipe_size,
                                position=position,
                                height=SUPPORT_DIMENSIONS.get(pipe_size, SUPPORT_DIMENSIONS[6])['shoe_height'],
                                load_capacity=self._get_load_capacity(pipe_size, 'shoe'),
                                brep=brep
                            ))

        # Generar bandeja de cables
        if include_tray and tray_tier < len(tier_heights):
            tray_height = tier_heights[tray_tier] + 50  # 50mm sobre el nivel

            # Crear bandeja a lo largo del rack
            for i in range(int(total_length / bay_spacing)):
                start_x = i * bay_spacing
                end_x = min((i + 1) * bay_spacing, total_length)

                tray_start = rg.Point3d(start_x, 0, tray_height)
                tray_end = rg.Point3d(end_x, 0, tray_height)

                tray_segment = self.tray_builder.create_tray_segment(
                    tray_start, tray_end, tray_width
                )

                if tray_segment:
                    all_tray.append(tray_segment)

        # Resumen
        result_summary = {
            'shoe_count': len(all_shoes),
            'guide_count': len(all_guides),
            'anchor_count': len(all_anchors),
            'hanger_count': len(all_hangers),
            'tray_segments': len(all_tray),
            'total_supports': len(support_list),
            'total_weight': total_weight,
            'support_spacing': support_spacing,
            'pipe_schedule': pipe_schedule
        }

        return SupportResult(
            shoes=all_shoes,
            guides=all_guides,
            anchors=all_anchors,
            hangers=all_hangers,
            cable_tray=all_tray,
            support_list=support_list,
            total_count=len(support_list),
            total_weight=total_weight,
            summary=result_summary
        )

    def _get_load_capacity(self, pipe_size, support_type):
        """Obtiene capacidad de carga del soporte (kg)."""
        base_capacity = {
            'shoe': {2: 100, 4: 200, 6: 350, 8: 500, 10: 700, 12: 900},
            'guide': {2: 150, 4: 300, 6: 500, 8: 750, 10: 1000, 12: 1300},
            'anchor': {2: 500, 4: 1000, 6: 1500, 8: 2000, 10: 2500, 12: 3000},
        }

        capacities = base_capacity.get(support_type, base_capacity['shoe'])
        sizes = sorted(capacities.keys())

        for s in sizes:
            if pipe_size <= s:
                return capacities[s]

        return capacities[max(sizes)]


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    builder = SupportBuilder(
        default_support_type=support_type if 'support_type' in dir() else 'shoe'
    )

    # Pipe schedule por defecto si no se proporciona
    default_schedule = [
        {'size': 6, 'count': 4, 'service': 'water', 'tier': 0},
        {'size': 4, 'count': 6, 'service': 'steam', 'tier': 1},
        {'size': 2, 'count': 8, 'service': 'gas', 'tier': 2},
    ]

    result = builder.build(
        rack_data=rack_data if 'rack_data' in dir() else None,
        pipe_schedule=pipe_schedule if 'pipe_schedule' in dir() else default_schedule,
        support_spacing=support_spacing if 'support_spacing' in dir() else 3000,
        insulation_gap=insulation_gap if 'insulation_gap' in dir() else 50,
        include_tray=include_tray if 'include_tray' in dir() else True,
        tray_width=tray_width if 'tray_width' in dir() else 600,
        tray_tier=tray_tier if 'tray_tier' in dir() else 0
    )

    # Salidas para Grasshopper
    shoes = result.shoes
    guides = result.guides
    anchors = result.anchors
    hangers = result.hangers
    cable_tray = result.cable_tray
    support_list = result.support_list
    total_count = result.total_count
    total_weight = result.total_weight
    summary = result.summary
