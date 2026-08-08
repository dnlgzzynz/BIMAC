"""
Rack Generator - Rack de Tuberias Parametrico
Genera la estructura principal del pipe rack.

Inputs:
    total_length (float): Longitud total (mm)
    bay_spacing (float): Espaciamiento entre marcos (mm)
    width (float): Ancho del rack (mm)
    height (float): Altura total (mm)
    tier_count (int): Numero de niveles
    tier_spacing (float): Espaciamiento entre niveles (mm)
    frame_type (str): Tipo de marco
    column_profile (str): Perfil de columnas
    beam_profile (str): Perfil de vigas

Outputs:
    columns (List[Brep]): Geometria de columnas
    beams (List[Brep]): Geometria de vigas
    bracing (List[Brep]): Geometria de arriostramientos
    structure_data (dict): Datos de la estructura
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de la estructura
RackData = namedtuple('RackData', [
    'columns', 'beams', 'struts', 'bracing',
    'tier_levels', 'bay_count', 'total_weight',
    'member_list', 'summary'
])

# Datos de miembro estructural
MemberData = namedtuple('MemberData', [
    'id', 'type', 'profile', 'start_point', 'end_point',
    'length', 'weight', 'brep'
])

# Perfiles estructurales (propiedades simplificadas)
PROFILE_DATA = {
    # W Shapes (imperial designation) - dimensions in mm
    'W6x15': {'d': 152, 'bf': 152, 'tf': 6.6, 'tw': 5.8, 'A': 2850, 'weight': 22.3},
    'W8x18': {'d': 203, 'bf': 133, 'tf': 7.2, 'tw': 5.8, 'A': 3420, 'weight': 26.8},
    'W10x22': {'d': 254, 'bf': 146, 'tf': 7.6, 'tw': 6.1, 'A': 4190, 'weight': 32.7},
    'W12x26': {'d': 305, 'bf': 165, 'tf': 8.5, 'tw': 6.4, 'A': 4950, 'weight': 38.7},
    'W12x40': {'d': 305, 'bf': 203, 'tf': 13.1, 'tw': 7.5, 'A': 7610, 'weight': 59.5},
    'W14x30': {'d': 356, 'bf': 171, 'tf': 10.0, 'tw': 6.9, 'A': 5710, 'weight': 44.6},
    'W14x48': {'d': 356, 'bf': 203, 'tf': 14.0, 'tw': 9.1, 'A': 9160, 'weight': 71.4},
    'W16x36': {'d': 406, 'bf': 178, 'tf': 10.9, 'tw': 7.5, 'A': 6840, 'weight': 53.6},
    # HSS (square tube)
    'HSS6x6x1/4': {'d': 152, 'bf': 152, 't': 6.4, 'A': 3550, 'weight': 21.6},
    'HSS8x8x5/16': {'d': 203, 'bf': 203, 't': 7.9, 'A': 6130, 'weight': 37.4},
    'HSS10x10x3/8': {'d': 254, 'bf': 254, 't': 9.5, 'A': 9420, 'weight': 58.1},
    'HSS12x12x1/2': {'d': 305, 'bf': 305, 't': 12.7, 'A': 14840, 'weight': 93.3},
    # Channels
    'C8x11.5': {'d': 203, 'bf': 57, 'tf': 9.9, 'tw': 6.5, 'A': 2200, 'weight': 17.1},
    'C10x15.3': {'d': 254, 'bf': 66, 'tf': 11.1, 'tw': 6.1, 'A': 2930, 'weight': 22.8},
    'C12x20.7': {'d': 305, 'bf': 74, 'tf': 12.6, 'tw': 7.2, 'A': 3950, 'weight': 30.8},
    # Angles
    'L3x3x1/4': {'d': 76, 'bf': 76, 't': 6.4, 'A': 929, 'weight': 7.11},
    'L4x4x3/8': {'d': 102, 'bf': 102, 't': 9.5, 'A': 1840, 'weight': 14.2},
    'L5x5x1/2': {'d': 127, 'bf': 127, 't': 12.7, 'A': 3060, 'weight': 23.6},
    'L6x6x1/2': {'d': 152, 'bf': 152, 't': 12.7, 'A': 3690, 'weight': 28.7},
}


class ProfileBuilder:
    """Construye perfiles estructurales."""

    def __init__(self):
        self.profiles = PROFILE_DATA

    def get_profile_data(self, profile_name):
        """Obtiene datos del perfil."""
        return self.profiles.get(profile_name, self.profiles['W8x18'])

    def create_w_profile(self, profile_name):
        """
        Crea perfil W (I-beam).

        Returns:
            Curve: Perfil cerrado del W shape
        """
        data = self.get_profile_data(profile_name)
        d = data['d']
        bf = data['bf']
        tf = data.get('tf', 10)
        tw = data.get('tw', 6)

        # Puntos del perfil I (simplificado sin filetes)
        points = [
            rg.Point3d(-bf/2, -d/2, 0),           # Bottom left
            rg.Point3d(bf/2, -d/2, 0),            # Bottom right
            rg.Point3d(bf/2, -d/2 + tf, 0),       # Bottom right inner
            rg.Point3d(tw/2, -d/2 + tf, 0),       # Web bottom right
            rg.Point3d(tw/2, d/2 - tf, 0),        # Web top right
            rg.Point3d(bf/2, d/2 - tf, 0),        # Top right inner
            rg.Point3d(bf/2, d/2, 0),             # Top right
            rg.Point3d(-bf/2, d/2, 0),            # Top left
            rg.Point3d(-bf/2, d/2 - tf, 0),       # Top left inner
            rg.Point3d(-tw/2, d/2 - tf, 0),       # Web top left
            rg.Point3d(-tw/2, -d/2 + tf, 0),      # Web bottom left
            rg.Point3d(-bf/2, -d/2 + tf, 0),      # Bottom left inner
            rg.Point3d(-bf/2, -d/2, 0),           # Close
        ]

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def create_hss_profile(self, profile_name):
        """
        Crea perfil HSS (tubo cuadrado).

        Returns:
            Curve: Perfil cerrado del HSS
        """
        data = self.get_profile_data(profile_name)
        d = data['d']
        bf = data.get('bf', d)
        t = data.get('t', 6)
        r = t * 1.5  # Radio de esquina

        # Rectangulo exterior
        outer = rg.Rectangle3d(
            rg.Plane.WorldXY,
            rg.Interval(-bf/2, bf/2),
            rg.Interval(-d/2, d/2)
        )

        # Para simplificar, retornamos solo el contorno exterior
        return outer.ToNurbsCurve()

    def create_channel_profile(self, profile_name):
        """
        Crea perfil C (canal).

        Returns:
            Curve: Perfil cerrado del canal
        """
        data = self.get_profile_data(profile_name)
        d = data['d']
        bf = data['bf']
        tf = data.get('tf', 10)
        tw = data.get('tw', 6)

        points = [
            rg.Point3d(0, -d/2, 0),
            rg.Point3d(bf, -d/2, 0),
            rg.Point3d(bf, -d/2 + tf, 0),
            rg.Point3d(tw, -d/2 + tf, 0),
            rg.Point3d(tw, d/2 - tf, 0),
            rg.Point3d(bf, d/2 - tf, 0),
            rg.Point3d(bf, d/2, 0),
            rg.Point3d(0, d/2, 0),
            rg.Point3d(0, -d/2, 0),
        ]

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def create_angle_profile(self, profile_name):
        """
        Crea perfil L (angulo).

        Returns:
            Curve: Perfil cerrado del angulo
        """
        data = self.get_profile_data(profile_name)
        d = data['d']
        bf = data.get('bf', d)
        t = data.get('t', 6)

        points = [
            rg.Point3d(0, 0, 0),
            rg.Point3d(bf, 0, 0),
            rg.Point3d(bf, t, 0),
            rg.Point3d(t, t, 0),
            rg.Point3d(t, d, 0),
            rg.Point3d(0, d, 0),
            rg.Point3d(0, 0, 0),
        ]

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def create_profile(self, profile_name):
        """Crea el perfil apropiado segun el nombre."""
        if profile_name.startswith('W'):
            return self.create_w_profile(profile_name)
        elif profile_name.startswith('HSS'):
            return self.create_hss_profile(profile_name)
        elif profile_name.startswith('C'):
            return self.create_channel_profile(profile_name)
        elif profile_name.startswith('L'):
            return self.create_angle_profile(profile_name)
        else:
            return self.create_w_profile('W8x18')


class FrameBuilder:
    """Construye marcos estructurales."""

    def __init__(self, profile_builder):
        self.profile_builder = profile_builder

    def create_member(self, start_point, end_point, profile_name, member_type='beam'):
        """
        Crea un miembro estructural.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            profile_name: Nombre del perfil
            member_type: Tipo de miembro

        Returns:
            Brep: Solido del miembro
        """
        # Crear linea guia
        axis = rg.Line(start_point, end_point)
        length = axis.Length

        # Crear perfil
        profile = self.profile_builder.create_profile(profile_name)

        # Orientar perfil al inicio
        direction = end_point - start_point
        direction.Unitize()

        # Plano perpendicular al eje
        if abs(direction.Z) > 0.9:
            up = rg.Vector3d.XAxis
        else:
            up = rg.Vector3d.ZAxis

        plane = rg.Plane(start_point, direction, rg.Vector3d.CrossProduct(direction, up))

        # Transformar perfil al plano
        xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        profile.Transform(xform)

        # Extruir
        extrusion = rg.Extrusion.Create(profile, length, True)

        if extrusion:
            return extrusion.ToBrep()
        return None

    def create_portal_frame(self, x_position, width, height, tier_heights,
                            column_profile, beam_profile, strut_profile):
        """
        Crea un marco portal en una posicion X.

        Args:
            x_position: Posicion X del marco
            width: Ancho del marco (Y)
            height: Altura total
            tier_heights: Lista de alturas de niveles
            column_profile: Perfil de columnas
            beam_profile: Perfil de vigas
            strut_profile: Perfil de puntales

        Returns:
            dict: Miembros del marco
        """
        members = {
            'columns': [],
            'beams': [],
            'struts': []
        }

        # Columnas (2 por marco)
        for y_offset in [-width/2, width/2]:
            col_start = rg.Point3d(x_position, y_offset, 0)
            col_end = rg.Point3d(x_position, y_offset, height)

            brep = self.create_member(col_start, col_end, column_profile, 'column')
            if brep:
                members['columns'].append({
                    'brep': brep,
                    'start': col_start,
                    'end': col_end,
                    'profile': column_profile,
                    'length': height
                })

        # Vigas principales (en cada nivel)
        for tier_h in tier_heights:
            beam_start = rg.Point3d(x_position, -width/2, tier_h)
            beam_end = rg.Point3d(x_position, width/2, tier_h)

            brep = self.create_member(beam_start, beam_end, beam_profile, 'beam')
            if brep:
                members['beams'].append({
                    'brep': brep,
                    'start': beam_start,
                    'end': beam_end,
                    'profile': beam_profile,
                    'length': width
                })

        return members

    def create_truss_frame(self, x_position, width, height, tier_heights,
                           column_profile, chord_profile, web_profile):
        """
        Crea un marco con armadura en la viga principal.

        Similar al portal pero con armadura en la viga superior.
        """
        members = self.create_portal_frame(
            x_position, width, height, tier_heights,
            column_profile, chord_profile, web_profile
        )

        # Agregar elementos de armadura en la viga superior
        top_tier = max(tier_heights)
        truss_depth = width * 0.08  # 8% del claro

        # Cuerda inferior
        chord_start = rg.Point3d(x_position, -width/2, top_tier - truss_depth)
        chord_end = rg.Point3d(x_position, width/2, top_tier - truss_depth)

        brep = self.create_member(chord_start, chord_end, chord_profile, 'chord')
        if brep:
            members['beams'].append({
                'brep': brep,
                'start': chord_start,
                'end': chord_end,
                'profile': chord_profile,
                'length': width
            })

        # Diagonales (simplificado)
        panel_count = 6
        panel_width = width / panel_count

        for i in range(panel_count):
            y1 = -width/2 + i * panel_width
            y2 = y1 + panel_width

            if i % 2 == 0:
                diag_start = rg.Point3d(x_position, y1, top_tier)
                diag_end = rg.Point3d(x_position, y2, top_tier - truss_depth)
            else:
                diag_start = rg.Point3d(x_position, y1, top_tier - truss_depth)
                diag_end = rg.Point3d(x_position, y2, top_tier)

            brep = self.create_member(diag_start, diag_end, web_profile, 'web')
            if brep:
                members['struts'].append({
                    'brep': brep,
                    'start': diag_start,
                    'end': diag_end,
                    'profile': web_profile,
                    'length': diag_start.DistanceTo(diag_end)
                })

        return members


class BracingBuilder:
    """Construye arriostramientos."""

    def __init__(self, profile_builder):
        self.profile_builder = profile_builder

    def create_x_bracing(self, bay_start_x, bay_end_x, y_position,
                         z_bottom, z_top, profile_name):
        """
        Crea arriostramiento en X.

        Returns:
            List[Brep]: Diagonales del arriostramiento
        """
        braces = []

        # Diagonal 1
        d1_start = rg.Point3d(bay_start_x, y_position, z_bottom)
        d1_end = rg.Point3d(bay_end_x, y_position, z_top)

        profile = self.profile_builder.create_profile(profile_name)
        axis = rg.Line(d1_start, d1_end)

        # Orientar perfil
        direction = d1_end - d1_start
        direction.Unitize()
        plane = rg.Plane(d1_start, direction)

        xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        profile1 = profile.Duplicate()
        profile1.Transform(xform)

        ext1 = rg.Extrusion.Create(profile1, axis.Length, True)
        if ext1:
            braces.append(ext1.ToBrep())

        # Diagonal 2
        d2_start = rg.Point3d(bay_end_x, y_position, z_bottom)
        d2_end = rg.Point3d(bay_start_x, y_position, z_top)

        direction2 = d2_end - d2_start
        direction2.Unitize()
        plane2 = rg.Plane(d2_start, direction2)

        profile2 = self.profile_builder.create_profile(profile_name)
        xform2 = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane2)
        profile2.Transform(xform2)

        ext2 = rg.Extrusion.Create(profile2, d2_start.DistanceTo(d2_end), True)
        if ext2:
            braces.append(ext2.ToBrep())

        return braces

    def create_v_bracing(self, bay_start_x, bay_end_x, y_position,
                         z_bottom, z_top, profile_name):
        """Crea arriostramiento en V."""
        braces = []
        mid_x = (bay_start_x + bay_end_x) / 2

        # Diagonal izquierda
        d1_start = rg.Point3d(bay_start_x, y_position, z_top)
        d1_end = rg.Point3d(mid_x, y_position, z_bottom)

        # Diagonal derecha
        d2_start = rg.Point3d(bay_end_x, y_position, z_top)
        d2_end = rg.Point3d(mid_x, y_position, z_bottom)

        for start, end in [(d1_start, d1_end), (d2_start, d2_end)]:
            profile = self.profile_builder.create_profile(profile_name)
            direction = end - start
            direction.Unitize()
            plane = rg.Plane(start, direction)

            xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
            profile.Transform(xform)

            ext = rg.Extrusion.Create(profile, start.DistanceTo(end), True)
            if ext:
                braces.append(ext.ToBrep())

        return braces


class LongitudinalBuilder:
    """Construye elementos longitudinales entre marcos."""

    def __init__(self, profile_builder):
        self.profile_builder = profile_builder

    def create_struts(self, bay_start_x, bay_end_x, width, tier_heights,
                      strut_profile):
        """
        Crea puntales longitudinales entre marcos.

        Returns:
            List[Brep]: Puntales
        """
        struts = []

        for tier_h in tier_heights:
            for y_offset in [-width/2, width/2]:
                strut_start = rg.Point3d(bay_start_x, y_offset, tier_h)
                strut_end = rg.Point3d(bay_end_x, y_offset, tier_h)

                profile = self.profile_builder.create_profile(strut_profile)
                direction = strut_end - strut_start
                direction.Unitize()
                plane = rg.Plane(strut_start, direction)

                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
                profile.Transform(xform)

                length = strut_start.DistanceTo(strut_end)
                ext = rg.Extrusion.Create(profile, length, True)

                if ext:
                    struts.append(ext.ToBrep())

        return struts


class PipeRackGenerator:
    """Generador principal de pipe rack."""

    def __init__(self, frame_type='portal_frame'):
        self.frame_type = frame_type
        self.profile_builder = ProfileBuilder()
        self.frame_builder = FrameBuilder(self.profile_builder)
        self.bracing_builder = BracingBuilder(self.profile_builder)
        self.longitudinal_builder = LongitudinalBuilder(self.profile_builder)

    def generate(self, total_length=30000, bay_spacing=6000, width=3000,
                 height=6000, tier_count=3, tier_spacing=1000,
                 first_tier_height=3500, column_profile='W12x26',
                 beam_profile='W10x22', strut_profile='W8x18',
                 bracing_profile='L4x4x3/8', bracing_type='X'):
        """
        Genera la estructura completa del pipe rack.

        Args:
            total_length: Longitud total (mm)
            bay_spacing: Espaciamiento entre marcos (mm)
            width: Ancho del rack (mm)
            height: Altura total (mm)
            tier_count: Numero de niveles
            tier_spacing: Espaciamiento entre niveles (mm)
            first_tier_height: Altura del primer nivel (mm)
            column_profile: Perfil de columnas
            beam_profile: Perfil de vigas
            strut_profile: Perfil de puntales
            bracing_profile: Perfil de arriostramientos
            bracing_type: Tipo de arriostramiento (X, V, K, none)

        Returns:
            RackData
        """
        all_columns = []
        all_beams = []
        all_struts = []
        all_bracing = []
        member_list = []

        # Calcular numero de crujias
        bay_count = max(1, int(total_length / bay_spacing))
        actual_bay_spacing = total_length / bay_count

        # Calcular alturas de niveles
        tier_heights = []
        for i in range(tier_count):
            tier_h = first_tier_height + i * tier_spacing
            tier_heights.append(tier_h)

        # Generar marcos
        frame_positions = [i * actual_bay_spacing for i in range(bay_count + 1)]

        total_weight = 0

        for x_pos in frame_positions:
            if self.frame_type == 'portal_frame':
                frame_members = self.frame_builder.create_portal_frame(
                    x_pos, width, height, tier_heights,
                    column_profile, beam_profile, strut_profile
                )
            elif self.frame_type == 'truss_frame':
                frame_members = self.frame_builder.create_truss_frame(
                    x_pos, width, height, tier_heights,
                    column_profile, beam_profile, strut_profile
                )
            else:
                frame_members = self.frame_builder.create_portal_frame(
                    x_pos, width, height, tier_heights,
                    column_profile, beam_profile, strut_profile
                )

            # Recolectar geometria
            for col in frame_members['columns']:
                all_columns.append(col['brep'])
                profile_data = self.profile_builder.get_profile_data(col['profile'])
                weight = col['length'] / 1000 * profile_data['weight']
                total_weight += weight

                member_list.append(MemberData(
                    id=f"COL-{len(member_list)+1:03d}",
                    type='column',
                    profile=col['profile'],
                    start_point=col['start'],
                    end_point=col['end'],
                    length=col['length'],
                    weight=weight,
                    brep=col['brep']
                ))

            for beam in frame_members['beams']:
                all_beams.append(beam['brep'])
                profile_data = self.profile_builder.get_profile_data(beam['profile'])
                weight = beam['length'] / 1000 * profile_data['weight']
                total_weight += weight

                member_list.append(MemberData(
                    id=f"BM-{len(member_list)+1:03d}",
                    type='beam',
                    profile=beam['profile'],
                    start_point=beam['start'],
                    end_point=beam['end'],
                    length=beam['length'],
                    weight=weight,
                    brep=beam['brep']
                ))

            for strut in frame_members.get('struts', []):
                all_struts.append(strut['brep'])

        # Generar puntales longitudinales entre marcos
        for i in range(len(frame_positions) - 1):
            x_start = frame_positions[i]
            x_end = frame_positions[i + 1]

            struts = self.longitudinal_builder.create_struts(
                x_start, x_end, width, tier_heights, strut_profile
            )

            for strut in struts:
                all_struts.append(strut)
                profile_data = self.profile_builder.get_profile_data(strut_profile)
                weight = actual_bay_spacing / 1000 * profile_data['weight']
                total_weight += weight

        # Generar arriostramientos
        if bracing_type != 'none':
            # Arriostramientos en planos laterales
            for i in range(len(frame_positions) - 1):
                x_start = frame_positions[i]
                x_end = frame_positions[i + 1]

                # Solo en crujias alternas
                if i % 2 == 0:
                    for y_offset in [-width/2, width/2]:
                        if bracing_type == 'X':
                            braces = self.bracing_builder.create_x_bracing(
                                x_start, x_end, y_offset,
                                0, first_tier_height, bracing_profile
                            )
                        elif bracing_type == 'V':
                            braces = self.bracing_builder.create_v_bracing(
                                x_start, x_end, y_offset,
                                0, first_tier_height, bracing_profile
                            )
                        else:
                            braces = []

                        all_bracing.extend(braces)

        # Resumen
        summary = {
            'total_length': total_length,
            'bay_count': bay_count,
            'bay_spacing': actual_bay_spacing,
            'width': width,
            'height': height,
            'tier_count': tier_count,
            'tier_heights': tier_heights,
            'frame_type': self.frame_type,
            'column_profile': column_profile,
            'beam_profile': beam_profile,
            'strut_profile': strut_profile,
            'bracing_type': bracing_type,
            'total_weight': total_weight,
            'frame_count': len(frame_positions),
            'column_count': len(all_columns),
            'beam_count': len(all_beams),
            'strut_count': len(all_struts),
            'bracing_count': len(all_bracing)
        }

        return RackData(
            columns=all_columns,
            beams=all_beams,
            struts=all_struts,
            bracing=all_bracing,
            tier_levels=tier_heights,
            bay_count=bay_count,
            total_weight=total_weight,
            member_list=member_list,
            summary=summary
        )


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    generator = PipeRackGenerator(
        frame_type=frame_type if 'frame_type' in dir() else 'portal_frame'
    )

    result = generator.generate(
        total_length=total_length if 'total_length' in dir() else 30000,
        bay_spacing=bay_spacing if 'bay_spacing' in dir() else 6000,
        width=width if 'width' in dir() else 3000,
        height=height if 'height' in dir() else 6000,
        tier_count=tier_count if 'tier_count' in dir() else 3,
        tier_spacing=tier_spacing if 'tier_spacing' in dir() else 1000,
        first_tier_height=first_tier_height if 'first_tier_height' in dir() else 3500,
        column_profile=column_profile if 'column_profile' in dir() else 'W12x26',
        beam_profile=beam_profile if 'beam_profile' in dir() else 'W10x22',
        strut_profile=strut_profile if 'strut_profile' in dir() else 'W8x18',
        bracing_profile=bracing_profile if 'bracing_profile' in dir() else 'L4x4x3/8',
        bracing_type=bracing_type if 'bracing_type' in dir() else 'X'
    )

    # Salidas para Grasshopper
    columns = result.columns
    beams = result.beams
    struts = result.struts
    bracing = result.bracing
    tier_levels = result.tier_levels
    bay_count = result.bay_count
    total_weight = result.total_weight
    member_list = result.member_list
    summary = result.summary
