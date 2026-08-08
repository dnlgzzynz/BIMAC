"""
Railing Builder - Escalera Helicoidal Parametrica
Genera barandales, pasamanos, balaustres y paneles.

Inputs:
    spiral_data (SpiralData): Datos de la espiral
    tread_data (List[TreadGeometry]): Datos de peldanos
    handrail_height (float): Altura de pasamanos (mm)
    handrail_diameter (float): Diametro de pasamanos (mm)
    baluster_type (str): Tipo de balaustre
    baluster_spacing (float): Espaciamiento (mm)
    infill_type (str): Tipo de relleno

Outputs:
    inner_handrail (Curve/Brep): Pasamanos interior
    outer_handrail (Curve/Brep): Pasamanos exterior
    balusters (List[Brep]): Balaustres
    infill (List[Brep]): Paneles de relleno
    railing_data (dict): Datos del barandal
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos del barandal
RailingData = namedtuple('RailingData', [
    'inner_handrail', 'outer_handrail', 'balusters',
    'infill_panels', 'posts', 'total_length',
    'baluster_count', 'weight', 'summary'
])

# Datos de balaustre
BalusterData = namedtuple('BalusterData', [
    'index', 'position', 'height', 'brep', 'type'
])


class HandrailBuilder:
    """Construye pasamanos helicoidales."""

    def __init__(self, diameter=42, material='steel'):
        """
        Args:
            diameter: Diametro del tubo (mm)
            material: Material del pasamanos
        """
        self.diameter = diameter
        self.material = material
        self.density = 7850 if material == 'steel' else 2700  # kg/m3

    def create_handrail_curve(self, spiral_data, height_offset, is_inner=True):
        """
        Crea la curva guia del pasamanos.

        Args:
            spiral_data: Datos de la espiral
            height_offset: Altura sobre el peldano (mm)
            is_inner: True para interior, False para exterior

        Returns:
            Curve: Curva helicoidal del pasamanos
        """
        stats = spiral_data.geometry_stats
        radius = (stats['inner_diameter'] / 2 + 50) if is_inner else (stats['outer_diameter'] / 2 - 50)

        # Parametros de la helice
        total_height = stats['floor_to_floor'] + height_offset
        total_rotation = math.radians(stats['total_rotation'])
        pitch = total_height / (total_rotation / (2 * math.pi))

        # Crear helice
        axis = rg.Line(rg.Point3d.Origin, rg.Point3d(0, 0, total_height))
        helix = rg.NurbsCurve.CreateSpiral(
            axis,
            radius,
            pitch,
            0,  # Start angle
            total_rotation,  # End angle
            True  # Counterclockwise
        )

        if helix:
            # Ajustar altura inicial
            transform = rg.Transform.Translation(0, 0, height_offset)
            helix.Transform(transform)

        return helix

    def create_handrail_solid(self, rail_curve):
        """
        Crea el solido del pasamanos por sweep.

        Args:
            rail_curve: Curva guia del pasamanos

        Returns:
            Brep: Solido del pasamanos
        """
        if rail_curve is None:
            return None

        # Crear perfil circular
        success, frame = rail_curve.PerpendicularFrameAt(rail_curve.Domain.T0)
        if not success:
            return None

        circle = rg.Circle(frame, self.diameter / 2)
        profile = circle.ToNurbsCurve()

        # Sweep
        sweep = rg.Brep.CreateFromSweep(
            rail_curve,
            profile,
            True,  # Cerrado
            0.01   # Tolerancia
        )

        if sweep and len(sweep) > 0:
            return sweep[0]
        return None

    def create_end_caps(self, rail_curve, cap_type='ball'):
        """
        Crea terminales del pasamanos.

        Args:
            rail_curve: Curva del pasamanos
            cap_type: 'ball', 'flat', 'return'

        Returns:
            List[Brep]: Terminales
        """
        caps = []

        if rail_curve is None:
            return caps

        # Puntos inicial y final
        start_pt = rail_curve.PointAtStart
        end_pt = rail_curve.PointAtEnd

        if cap_type == 'ball':
            # Esferas decorativas
            ball_radius = self.diameter * 0.75
            start_sphere = rg.Sphere(start_pt, ball_radius)
            end_sphere = rg.Sphere(end_pt, ball_radius)
            caps.append(start_sphere.ToBrep())
            caps.append(end_sphere.ToBrep())

        elif cap_type == 'flat':
            # Tapas planas
            success, start_frame = rail_curve.PerpendicularFrameAt(
                rail_curve.Domain.T0
            )
            if success:
                cap_circle = rg.Circle(start_frame, self.diameter / 2)
                cap_brep = rg.Brep.CreatePlanarBreps(
                    cap_circle.ToNurbsCurve(), 0.01
                )
                if cap_brep:
                    caps.extend(cap_brep)

        return caps

    def calculate_weight(self, rail_curve):
        """Calcula peso del pasamanos."""
        if rail_curve is None:
            return 0

        length = rail_curve.GetLength() / 1000  # m
        area = math.pi * (self.diameter / 2000) ** 2  # m2
        volume = area * length  # m3
        return volume * self.density


class BalusterBuilder:
    """Construye balaustres."""

    # Tipos de balaustres
    BALUSTER_TYPES = {
        'round': {'diameter': 16, 'shape': 'circle'},
        'square': {'side': 14, 'shape': 'square'},
        'flat': {'width': 30, 'thickness': 6, 'shape': 'rectangle'},
        'decorative': {'diameter': 20, 'shape': 'turned'}
    }

    def __init__(self, baluster_type='round', material='steel'):
        self.baluster_type = baluster_type
        self.material = material
        self.config = self.BALUSTER_TYPES.get(baluster_type, self.BALUSTER_TYPES['round'])
        self.density = 7850 if material == 'steel' else 700  # kg/m3

    def create_baluster_profile(self):
        """Crea el perfil del balaustre."""
        shape = self.config.get('shape', 'circle')

        if shape == 'circle':
            radius = self.config.get('diameter', 16) / 2
            return rg.Circle(rg.Plane.WorldXY, radius).ToNurbsCurve()

        elif shape == 'square':
            side = self.config.get('side', 14)
            rect = rg.Rectangle3d(
                rg.Plane.WorldXY,
                rg.Interval(-side / 2, side / 2),
                rg.Interval(-side / 2, side / 2)
            )
            return rect.ToNurbsCurve()

        elif shape == 'rectangle':
            width = self.config.get('width', 30)
            thickness = self.config.get('thickness', 6)
            rect = rg.Rectangle3d(
                rg.Plane.WorldXY,
                rg.Interval(-width / 2, width / 2),
                rg.Interval(-thickness / 2, thickness / 2)
            )
            return rect.ToNurbsCurve()

        else:
            # Default circular
            return rg.Circle(rg.Plane.WorldXY, 8).ToNurbsCurve()

    def create_baluster(self, base_point, height, angle=0):
        """
        Crea un balaustre individual.

        Args:
            base_point: Punto base (sobre peldano)
            height: Altura del balaustre (mm)
            angle: Angulo de rotacion (radianes)

        Returns:
            Brep: Solido del balaustre
        """
        profile = self.create_baluster_profile()

        # Posicionar perfil
        base_plane = rg.Plane(base_point, rg.Vector3d.ZAxis)
        base_plane.Rotate(angle, rg.Vector3d.ZAxis)

        transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, base_plane)
        profile.Transform(transform)

        # Extruir
        extrusion = rg.Extrusion.Create(profile, height, True)

        if extrusion:
            return extrusion.ToBrep()
        return None

    def distribute_on_tread(self, tread_pos, inner_radius, outer_radius,
                            angle_start, angle_end, spacing, height):
        """
        Distribuye balaustres sobre un peldano.

        Args:
            tread_pos: Posicion del peldano
            inner_radius: Radio interior (mm)
            outer_radius: Radio exterior (mm)
            angle_start: Angulo inicial (radianes)
            angle_end: Angulo final (radianes)
            spacing: Espaciamiento maximo (mm)
            height: Altura del balaustre (mm)

        Returns:
            List[BalusterData]: Datos de balaustres
        """
        balusters = []

        # Calcular numero de balaustres por arco
        arc_length = (outer_radius + inner_radius) / 2 * abs(angle_end - angle_start)
        count = max(2, int(arc_length / spacing) + 1)

        # Posicion en radio medio
        mid_radius = (inner_radius + outer_radius) / 2

        for i in range(count):
            t = i / max(1, count - 1)
            angle = angle_start + t * (angle_end - angle_start)

            x = mid_radius * math.cos(angle)
            y = mid_radius * math.sin(angle)
            z = tread_pos.height

            base_pt = rg.Point3d(x, y, z)
            brep = self.create_baluster(base_pt, height, angle)

            if brep:
                data = BalusterData(
                    index=len(balusters),
                    position=base_pt,
                    height=height,
                    brep=brep,
                    type=self.baluster_type
                )
                balusters.append(data)

        return balusters


class InfillBuilder:
    """Construye paneles de relleno."""

    INFILL_TYPES = {
        'balusters': 'Solo balaustres',
        'glass': 'Panel de vidrio',
        'cable': 'Cables horizontales',
        'mesh': 'Malla metalica',
        'perforated': 'Lamina perforada'
    }

    def __init__(self, infill_type='balusters'):
        self.infill_type = infill_type

    def create_glass_panel(self, inner_curve, outer_curve, height,
                           glass_thickness=12):
        """
        Crea panel de vidrio entre curvas.

        Args:
            inner_curve: Curva interior
            outer_curve: Curva exterior
            height: Altura del panel (mm)
            glass_thickness: Espesor del vidrio (mm)

        Returns:
            Brep: Panel de vidrio
        """
        if inner_curve is None or outer_curve is None:
            return None

        # Crear superficie loft entre curvas
        curves = [inner_curve, outer_curve]
        loft = rg.Brep.CreateFromLoft(
            curves,
            rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal,
            False
        )

        if loft and len(loft) > 0:
            # Extruir hacia arriba
            surface = loft[0]
            panel = rg.Brep.CreateOffsetBrep(
                surface,
                glass_thickness,
                True,  # Solid
                True,  # Both sides
                0.01
            )
            if panel and len(panel) > 0:
                return panel[0]

        return None

    def create_cable_infill(self, start_plane, end_plane, height,
                            cable_diameter=4, cable_spacing=75):
        """
        Crea cables horizontales de relleno.

        Args:
            start_plane: Plano inicial
            end_plane: Plano final
            height: Altura total (mm)
            cable_diameter: Diametro del cable (mm)
            cable_spacing: Espaciamiento vertical (mm)

        Returns:
            List[Brep]: Cables
        """
        cables = []
        cable_count = int(height / cable_spacing)

        for i in range(1, cable_count):
            z_offset = i * cable_spacing

            # Puntos del cable
            start_pt = start_plane.Origin + rg.Vector3d(0, 0, z_offset)
            end_pt = end_plane.Origin + rg.Vector3d(0, 0, z_offset)

            # Crear linea y tuberia
            line = rg.Line(start_pt, end_pt)
            circle = rg.Circle(
                rg.Plane(start_pt, line.Direction),
                cable_diameter / 2
            )

            pipe = rg.Brep.CreatePipe(
                line.ToNurbsCurve(),
                cable_diameter / 2,
                False,  # No local blending
                rg.PipeCapMode.Flat,
                True,  # Fit rail
                0.01,
                0.01
            )

            if pipe and len(pipe) > 0:
                cables.append(pipe[0])

        return cables

    def create_mesh_panel(self, boundary_curve, height, opening_size=50):
        """
        Crea panel de malla metalica.

        Args:
            boundary_curve: Curva de borde
            height: Altura del panel
            opening_size: Tamano de apertura (mm)

        Returns:
            Brep: Panel de malla (simplificado como superficie)
        """
        if boundary_curve is None:
            return None

        # Por ahora, crear superficie simple
        # En implementacion completa, generar patron de malla
        extrusion = rg.Extrusion.Create(boundary_curve, height, True)

        if extrusion:
            return extrusion.ToBrep()
        return None


class PostBuilder:
    """Construye postes estructurales."""

    def __init__(self, post_diameter=50, material='steel'):
        self.post_diameter = post_diameter
        self.material = material

    def create_post(self, base_point, height):
        """
        Crea un poste estructural.

        Args:
            base_point: Punto base
            height: Altura del poste (mm)

        Returns:
            Brep: Solido del poste
        """
        circle = rg.Circle(
            rg.Plane(base_point, rg.Vector3d.ZAxis),
            self.post_diameter / 2
        )

        extrusion = rg.Extrusion.Create(
            circle.ToNurbsCurve(),
            height,
            True
        )

        if extrusion:
            return extrusion.ToBrep()
        return None

    def distribute_posts(self, spiral_data, height, post_interval=3):
        """
        Distribuye postes a lo largo de la escalera.

        Args:
            spiral_data: Datos de la espiral
            height: Altura de los postes (mm)
            post_interval: Intervalo en numero de peldanos

        Returns:
            List[Brep]: Postes
        """
        posts = []
        stats = spiral_data.geometry_stats
        outer_radius = stats['outer_diameter'] / 2 - 25

        for i, tread_pos in enumerate(spiral_data.tread_points):
            if i % post_interval == 0:
                angle = math.radians(tread_pos.angle)
                x = outer_radius * math.cos(angle)
                y = outer_radius * math.sin(angle)

                base_pt = rg.Point3d(x, y, tread_pos.height)
                post = self.create_post(base_pt, height)

                if post:
                    posts.append(post)

        return posts


class RailingBuilder:
    """Constructor principal de barandales."""

    def __init__(self, handrail_diameter=42, baluster_type='round',
                 infill_type='balusters', material='steel'):
        self.handrail_builder = HandrailBuilder(handrail_diameter, material)
        self.baluster_builder = BalusterBuilder(baluster_type, material)
        self.infill_builder = InfillBuilder(infill_type)
        self.post_builder = PostBuilder(50, material)
        self.material = material

    def build(self, spiral_data, handrail_height=1000, baluster_spacing=120,
              inner_railing=True, outer_railing=True):
        """
        Construye el sistema completo de barandales.

        Args:
            spiral_data: Datos de la espiral
            handrail_height: Altura del pasamanos (mm)
            baluster_spacing: Espaciamiento de balaustres (mm)
            inner_railing: Incluir barandal interior
            outer_railing: Incluir barandal exterior

        Returns:
            RailingData
        """
        stats = spiral_data.geometry_stats
        inner_radius = stats['inner_diameter'] / 2
        outer_radius = stats['outer_diameter'] / 2
        rotation_per_tread = math.radians(stats['rotation_per_tread'])

        # Pasamanos
        inner_handrail = None
        outer_handrail = None
        inner_handrail_brep = None
        outer_handrail_brep = None

        if inner_railing:
            inner_handrail = self.handrail_builder.create_handrail_curve(
                spiral_data, handrail_height, is_inner=True
            )
            inner_handrail_brep = self.handrail_builder.create_handrail_solid(
                inner_handrail
            )

        if outer_railing:
            outer_handrail = self.handrail_builder.create_handrail_curve(
                spiral_data, handrail_height, is_inner=False
            )
            outer_handrail_brep = self.handrail_builder.create_handrail_solid(
                outer_handrail
            )

        # Balaustres
        all_balusters = []
        baluster_breps = []

        for i, tread_pos in enumerate(spiral_data.tread_points[:-1]):
            angle_start = math.radians(tread_pos.angle)
            angle_end = angle_start + rotation_per_tread

            # Balaustres en borde exterior
            if outer_railing:
                balusters = self.baluster_builder.distribute_on_tread(
                    tread_pos,
                    outer_radius - 75,
                    outer_radius - 25,
                    angle_start, angle_end,
                    baluster_spacing,
                    handrail_height - 50
                )
                all_balusters.extend(balusters)
                baluster_breps.extend([b.brep for b in balusters if b.brep])

            # Balaustres en borde interior
            if inner_railing:
                balusters = self.baluster_builder.distribute_on_tread(
                    tread_pos,
                    inner_radius + 25,
                    inner_radius + 75,
                    angle_start, angle_end,
                    baluster_spacing,
                    handrail_height - 50
                )
                all_balusters.extend(balusters)
                baluster_breps.extend([b.brep for b in balusters if b.brep])

        # Postes estructurales
        posts = self.post_builder.distribute_posts(
            spiral_data, handrail_height, post_interval=4
        )

        # Paneles de relleno (si aplica)
        infill_panels = []
        if self.infill_builder.infill_type != 'balusters':
            # Implementar segun tipo
            pass

        # Calcular longitudes y pesos
        inner_length = inner_handrail.GetLength() if inner_handrail else 0
        outer_length = outer_handrail.GetLength() if outer_handrail else 0
        total_length = (inner_length + outer_length) / 1000  # m

        # Peso estimado
        handrail_weight = (
            self.handrail_builder.calculate_weight(inner_handrail) +
            self.handrail_builder.calculate_weight(outer_handrail)
        )

        baluster_weight = len(all_balusters) * 0.5  # ~0.5 kg por balaustre
        post_weight = len(posts) * 3.0  # ~3 kg por poste
        total_weight = handrail_weight + baluster_weight + post_weight

        # Resumen
        summary = {
            'inner_railing': inner_railing,
            'outer_railing': outer_railing,
            'handrail_diameter': self.handrail_builder.diameter,
            'handrail_height': handrail_height,
            'baluster_type': self.baluster_builder.baluster_type,
            'baluster_count': len(all_balusters),
            'baluster_spacing': baluster_spacing,
            'post_count': len(posts),
            'total_length': total_length,
            'total_weight': total_weight,
            'material': self.material
        }

        return RailingData(
            inner_handrail=inner_handrail_brep,
            outer_handrail=outer_handrail_brep,
            balusters=baluster_breps,
            infill_panels=infill_panels,
            posts=posts,
            total_length=total_length,
            baluster_count=len(all_balusters),
            weight=total_weight,
            summary=summary
        )


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    builder = RailingBuilder(
        handrail_diameter=handrail_diameter if 'handrail_diameter' in dir() else 42,
        baluster_type=baluster_type if 'baluster_type' in dir() else 'round',
        infill_type=infill_type if 'infill_type' in dir() else 'balusters',
        material=handrail_material if 'handrail_material' in dir() else 'steel'
    )

    result = builder.build(
        spiral_data=spiral_data if 'spiral_data' in dir() else None,
        handrail_height=handrail_height if 'handrail_height' in dir() else 1000,
        baluster_spacing=baluster_spacing if 'baluster_spacing' in dir() else 120,
        inner_railing=inner_handrail if 'inner_handrail' in dir() else True,
        outer_railing=outer_handrail if 'outer_handrail' in dir() else True
    )

    # Salidas para Grasshopper
    inner_handrail = result.inner_handrail
    outer_handrail = result.outer_handrail
    balusters = result.balusters
    infill = result.infill_panels
    posts = result.posts
    railing_data = result.summary
    total_weight = result.weight
