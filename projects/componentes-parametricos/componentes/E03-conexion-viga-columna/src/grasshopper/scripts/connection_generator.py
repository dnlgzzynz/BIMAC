"""
Connection Generator - Conexion Viga-Columna Parametrica
Genera conexiones estructurales viga-columna.

Inputs:
    beam_profile (str): Perfil de viga (W18x50)
    column_profile (str): Perfil de columna (W14x90)
    connection_type (str): Tipo de conexion
    seismic_category (str): Categoria sismica (SMF, IMF, OMF, none)
    bolt_diameter (int): Diametro de tornillos (mm)
    bolt_grade (str): Grado de tornillos (A325, A490)

Outputs:
    plates (List[Brep]): Placas de conexion
    bolts (List[Brep]): Tornillos
    welds (List[Curve]): Lineas de soldadura
    stiffeners (List[Brep]): Rigidizadores
    connection_data (dict): Datos de la conexion
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de la conexion
ConnectionData = namedtuple('ConnectionData', [
    'type', 'beam_profile', 'column_profile',
    'plates', 'bolts', 'welds', 'stiffeners',
    'shear_capacity', 'moment_capacity', 'weight', 'summary'
])

# Datos de perfil W
ProfileData = namedtuple('ProfileData', [
    'name', 'd', 'bf', 'tf', 'tw', 'k', 'Zx', 'weight'
])

# Base de datos de perfiles
PROFILE_DATABASE = {
    # Vigas
    'W12x26': ProfileData('W12x26', 310, 165, 9.7, 6.4, 24, 402, 38.7),
    'W14x30': ProfileData('W14x30', 352, 171, 9.8, 6.9, 27, 542, 44.6),
    'W16x36': ProfileData('W16x36', 403, 178, 10.9, 7.5, 30, 764, 53.6),
    'W18x50': ProfileData('W18x50', 457, 190, 14.5, 9.0, 35, 1130, 74.4),
    'W21x62': ProfileData('W21x62', 533, 209, 15.6, 10.2, 40, 1670, 92.3),
    'W24x76': ProfileData('W24x76', 607, 229, 17.3, 11.2, 44, 2400, 113.1),
    'W27x94': ProfileData('W27x94', 684, 254, 19.0, 12.4, 48, 3410, 140.0),
    'W30x116': ProfileData('W30x116', 762, 267, 21.6, 14.0, 53, 4630, 172.7),
    'W33x130': ProfileData('W33x130', 841, 292, 21.7, 14.0, 54, 5630, 193.5),
    'W36x150': ProfileData('W36x150', 912, 305, 23.9, 15.9, 59, 7100, 223.3),
    # Columnas
    'W10x49': ProfileData('W10x49', 254, 254, 14.2, 8.6, 35, 717, 72.9),
    'W12x65': ProfileData('W12x65', 308, 305, 15.4, 9.9, 38, 1060, 96.8),
    'W14x90': ProfileData('W14x90', 356, 368, 18.0, 11.2, 43, 1590, 134.0),
    'W14x132': ProfileData('W14x132', 373, 373, 26.2, 16.4, 53, 2420, 196.4),
    'W14x176': ProfileData('W14x176', 394, 399, 33.3, 21.1, 64, 3360, 261.9),
    'W14x257': ProfileData('W14x257', 417, 406, 48.0, 30.0, 83, 5050, 382.5),
    'W14x370': ProfileData('W14x370', 455, 419, 67.6, 42.2, 108, 7520, 550.7),
}


class PlateBuilder:
    """Construye placas de conexion."""

    def __init__(self, material='A36'):
        self.material = material
        self.Fy = 250 if material == 'A36' else 345  # MPa

    def create_shear_tab(self, beam, column, bolt_rows, bolt_diameter,
                          thickness=10, setback=12):
        """
        Crea shear tab (placa simple).

        Args:
            beam: Datos del perfil de viga
            column: Datos del perfil de columna
            bolt_rows: Numero de filas de tornillos
            bolt_diameter: Diametro de tornillos (mm)
            thickness: Espesor de placa (mm)
            setback: Distancia del borde superior (mm)

        Returns:
            Brep: Geometria de la placa
        """
        # Dimensiones
        edge_dist = self._get_edge_distance(bolt_diameter)
        spacing = bolt_diameter * 3
        plate_height = 2 * edge_dist + (bolt_rows - 1) * spacing
        plate_width = 2 * edge_dist + bolt_diameter

        # Posicion (en cara de columna)
        x_pos = column.bf / 2 + thickness / 2
        y_pos = 0
        z_pos = beam.d / 2 - setback - plate_height / 2

        # Crear placa
        center = rg.Point3d(x_pos, y_pos, z_pos)
        plane = rg.Plane(center, rg.Vector3d.XAxis)

        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-plate_height / 2, plate_height / 2),
            rg.Interval(-plate_width / 2, plate_width / 2)
        )

        extrusion = rg.Extrusion.Create(
            rect.ToNurbsCurve(),
            thickness,
            True
        )

        if extrusion:
            return extrusion.ToBrep()
        return None

    def create_end_plate(self, beam, thickness=25, extended_top=0,
                          extended_bottom=0):
        """
        Crea end plate (placa de extremo).

        Args:
            beam: Datos del perfil de viga
            thickness: Espesor de placa (mm)
            extended_top: Extension arriba del patin (mm)
            extended_bottom: Extension abajo del patin (mm)

        Returns:
            Brep: Geometria de la placa
        """
        # Dimensiones
        plate_height = beam.d + extended_top + extended_bottom
        plate_width = beam.bf + 50  # 25mm cada lado

        # Posicion (al final de la viga)
        x_pos = 0
        y_pos = 0
        z_pos = extended_bottom - beam.d / 2

        center = rg.Point3d(x_pos, y_pos, z_pos + plate_height / 2)
        plane = rg.Plane(center, rg.Vector3d.XAxis)

        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-plate_height / 2, plate_height / 2),
            rg.Interval(-plate_width / 2, plate_width / 2)
        )

        extrusion = rg.Extrusion.Create(
            rect.ToNurbsCurve(),
            thickness,
            True
        )

        if extrusion:
            # Mover a posicion correcta
            brep = extrusion.ToBrep()
            xform = rg.Transform.Translation(-thickness / 2, 0, 0)
            brep.Transform(xform)
            return brep
        return None

    def create_continuity_plate(self, column, beam, position='top'):
        """
        Crea placa de continuidad.

        Args:
            column: Datos del perfil de columna
            beam: Datos del perfil de viga
            position: 'top' o 'bottom'

        Returns:
            Brep: Geometria de la placa
        """
        # Dimensiones
        # Ancho: desde alma hasta borde de patin - clip
        width = (column.bf - column.tw) / 2 - 25  # 25mm clip
        height = column.d - 2 * column.k  # Entre filetes
        thickness = max(beam.tf, 12)  # Al menos igual al patin de viga

        # Posicion Z
        if position == 'top':
            z_pos = beam.d / 2 - beam.tf / 2
        else:
            z_pos = -beam.d / 2 + beam.tf / 2

        plates = []

        # Crear dos placas (una a cada lado del alma)
        for side in [-1, 1]:
            x_pos = 0
            y_pos = side * (column.tw / 2 + width / 2)

            center = rg.Point3d(x_pos, y_pos, z_pos)
            plane = rg.Plane(center, rg.Vector3d.ZAxis)

            rect = rg.Rectangle3d(
                plane,
                rg.Interval(-height / 2, height / 2),
                rg.Interval(-width / 2, width / 2)
            )

            extrusion = rg.Extrusion.Create(
                rect.ToNurbsCurve(),
                thickness,
                True
            )

            if extrusion:
                brep = extrusion.ToBrep()
                xform = rg.Transform.Translation(0, 0, -thickness / 2)
                brep.Transform(xform)
                plates.append(brep)

        return plates

    def create_doubler_plate(self, column, beam, thickness=12):
        """
        Crea placa de refuerzo (doubler plate).

        Args:
            column: Datos del perfil de columna
            beam: Datos del perfil de viga
            thickness: Espesor de la placa (mm)

        Returns:
            Brep: Geometria de la placa
        """
        # Dimensiones (cubre panel zone)
        height = beam.d - 2 * beam.tf + 100  # Panel zone + extension
        width = column.d - 2 * column.k  # Entre filetes

        # Posicion (en alma de columna)
        center = rg.Point3d(0, column.tw / 2 + thickness / 2, 0)
        plane = rg.Plane(center, rg.Vector3d.YAxis)

        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-width / 2, width / 2),
            rg.Interval(-height / 2, height / 2)
        )

        extrusion = rg.Extrusion.Create(
            rect.ToNurbsCurve(),
            thickness,
            True
        )

        if extrusion:
            return extrusion.ToBrep()
        return None

    def _get_edge_distance(self, bolt_diameter):
        """Obtiene distancia al borde minima."""
        edge_distances = {
            16: 28, 20: 34, 22: 38, 24: 42, 27: 48, 30: 52, 36: 62
        }
        return edge_distances.get(bolt_diameter, 38)


class BoltBuilder:
    """Construye tornillos."""

    BOLT_DIMENSIONS = {
        16: {'head_dia': 27, 'head_height': 10, 'nut_height': 13},
        20: {'head_dia': 34, 'head_height': 13, 'nut_height': 16},
        22: {'head_dia': 36, 'head_height': 14, 'nut_height': 18},
        24: {'head_dia': 41, 'head_height': 15, 'nut_height': 19},
        27: {'head_dia': 46, 'head_height': 17, 'nut_height': 22},
        30: {'head_dia': 50, 'head_height': 19, 'nut_height': 24},
    }

    def __init__(self, diameter=22, grade='A325'):
        self.diameter = diameter
        self.grade = grade
        self.dims = self.BOLT_DIMENSIONS.get(diameter, self.BOLT_DIMENSIONS[22])

    def create_bolt(self, position, grip_length):
        """
        Crea un tornillo completo (cabeza + vastago + tuerca).

        Args:
            position: Punto de insercion
            grip_length: Longitud de agarre (mm)

        Returns:
            Brep: Geometria del tornillo
        """
        breps = []

        # Cabeza hexagonal (simplificada como cilindro)
        head_plane = rg.Plane(position, rg.Vector3d.XAxis)
        head = rg.Cylinder(
            rg.Circle(head_plane, self.dims['head_dia'] / 2),
            -self.dims['head_height']
        )
        breps.append(head.ToBrep(True, True))

        # Vastago
        shank_length = grip_length + self.dims['nut_height'] + 5
        shank = rg.Cylinder(
            rg.Circle(head_plane, self.diameter / 2),
            shank_length
        )
        breps.append(shank.ToBrep(True, True))

        # Tuerca
        nut_plane = rg.Plane(
            rg.Point3d(
                position.X + grip_length,
                position.Y,
                position.Z
            ),
            rg.Vector3d.XAxis
        )
        nut = rg.Cylinder(
            rg.Circle(nut_plane, self.dims['head_dia'] / 2),
            self.dims['nut_height']
        )
        breps.append(nut.ToBrep(True, True))

        # Unir
        joined = rg.Brep.JoinBreps(breps, 0.01)
        if joined and len(joined) > 0:
            return joined[0]

        return breps[0] if breps else None

    def create_bolt_pattern(self, center, rows, cols, row_spacing, col_spacing,
                            grip_length):
        """
        Crea patron de tornillos.

        Args:
            center: Centro del patron
            rows: Numero de filas (vertical)
            cols: Numero de columnas (horizontal)
            row_spacing: Espaciamiento vertical (mm)
            col_spacing: Espaciamiento horizontal (mm)
            grip_length: Longitud de agarre (mm)

        Returns:
            List[Brep]: Lista de tornillos
        """
        bolts = []

        # Calcular offset para centrar
        y_offset = -(cols - 1) * col_spacing / 2
        z_offset = -(rows - 1) * row_spacing / 2

        for i in range(rows):
            for j in range(cols):
                y = center.Y + y_offset + j * col_spacing
                z = center.Z + z_offset + i * row_spacing

                bolt_pos = rg.Point3d(center.X, y, z)
                bolt = self.create_bolt(bolt_pos, grip_length)

                if bolt:
                    bolts.append(bolt)

        return bolts


class WeldBuilder:
    """Construye representacion de soldaduras."""

    def __init__(self, electrode='E70'):
        self.electrode = electrode
        self.Fexx = 482 if electrode == 'E70' else 551  # MPa

    def create_fillet_weld_line(self, start_point, end_point, size, both_sides=True):
        """
        Crea lineas de soldadura de filete.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            size: Tamano del filete (mm)
            both_sides: Soldadura a ambos lados

        Returns:
            List[Curve]: Lineas de soldadura
        """
        lines = []

        # Linea principal
        line = rg.Line(start_point, end_point)
        lines.append(line.ToNurbsCurve())

        # Agregar simbolo de tamano (simplificado)
        # En implementacion completa, agregar anotacion

        return lines

    def create_CJP_weld_line(self, curve, access_hole=False):
        """
        Crea linea de soldadura CJP.

        Args:
            curve: Curva de la junta
            access_hole: Incluye access hole

        Returns:
            Curve: Linea de soldadura
        """
        return curve

    def get_minimum_fillet_size(self, thicker_plate):
        """Obtiene tamano minimo de filete segun AWS D1.1."""
        if thicker_plate <= 6:
            return 3
        elif thicker_plate <= 13:
            return 5
        elif thicker_plate <= 19:
            return 6
        else:
            return 8


class RBSBuilder:
    """Construye Reduced Beam Section."""

    def __init__(self):
        pass

    def calculate_rbs_dimensions(self, beam):
        """
        Calcula dimensiones del corte RBS segun AISC 358.

        Args:
            beam: Datos del perfil de viga

        Returns:
            dict: Dimensiones del corte
        """
        bf = beam.bf
        d = beam.d

        # Limites AISC 358
        # a: distancia del face de columna al inicio del corte
        a_min = 0.5 * bf
        a_max = 0.75 * bf
        a = 0.625 * bf  # Valor tipico

        # b: longitud del corte
        b_min = 0.65 * d
        b_max = 0.85 * d
        b = 0.75 * d  # Valor tipico

        # c: profundidad del corte en cada lado
        c_min = 0.1 * bf
        c_max = 0.25 * bf
        c = 0.2 * bf  # Valor tipico (40% reduccion total)

        return {
            'a': a,
            'b': b,
            'c': c,
            'a_min': a_min,
            'a_max': a_max,
            'b_min': b_min,
            'b_max': b_max,
            'c_min': c_min,
            'c_max': c_max,
            'Zrbs': beam.Zx * (1 - 2 * c / bf)  # Modulo plastico reducido
        }

    def create_rbs_cut(self, beam, position='top'):
        """
        Crea geometria del corte RBS.

        Args:
            beam: Datos del perfil de viga
            position: 'top' o 'bottom'

        Returns:
            Brep: Volumen a remover
        """
        dims = self.calculate_rbs_dimensions(beam)

        # Crear curva del corte (arco circular)
        # El corte es un arco que remueve 'c' del patin

        # Calcular radio del arco
        # Usando geometria: R = (b^2 + 4c^2) / (8c)
        R = (dims['b']**2 + 4 * dims['c']**2) / (8 * dims['c'])

        # Centro del arco
        x_center = dims['a'] + dims['b'] / 2
        z_sign = 1 if position == 'top' else -1
        y_center = z_sign * (beam.bf / 2 - dims['c'] + R)

        # Puntos del arco
        arc_start = rg.Point3d(x_center - dims['b']/2, z_sign * beam.bf/2, 0)
        arc_mid = rg.Point3d(x_center, z_sign * (beam.bf/2 - dims['c']), 0)
        arc_end = rg.Point3d(x_center + dims['b']/2, z_sign * beam.bf/2, 0)

        arc = rg.Arc(arc_start, arc_mid, arc_end)

        # Extruir el corte a traves del espesor del patin
        if position == 'top':
            z_pos = beam.d / 2 - beam.tf
        else:
            z_pos = -beam.d / 2

        # Transformar a posicion correcta
        # Simplificado: retornar solo las dimensiones por ahora

        return dims


class ConnectionGenerator:
    """Generador principal de conexiones."""

    def __init__(self, connection_type='shear_tab', seismic_category='none'):
        self.connection_type = connection_type
        self.seismic_category = seismic_category
        self.plate_builder = PlateBuilder()
        self.bolt_builder = None
        self.weld_builder = WeldBuilder()
        self.rbs_builder = RBSBuilder()

    def generate(self, beam_profile, column_profile, bolt_diameter=22,
                 bolt_grade='A325', beam_material='A992', column_material='A992'):
        """
        Genera conexion completa.

        Args:
            beam_profile: Nombre del perfil de viga
            column_profile: Nombre del perfil de columna
            bolt_diameter: Diametro de tornillos (mm)
            bolt_grade: Grado de tornillos
            beam_material: Material de viga
            column_material: Material de columna

        Returns:
            ConnectionData
        """
        # Obtener datos de perfiles
        beam = PROFILE_DATABASE.get(beam_profile)
        column = PROFILE_DATABASE.get(column_profile)

        if beam is None or column is None:
            return None

        self.bolt_builder = BoltBuilder(bolt_diameter, bolt_grade)

        plates = []
        bolts = []
        welds = []
        stiffeners = []

        # Generar segun tipo
        if self.connection_type == 'shear_tab':
            result = self._generate_shear_tab(beam, column, bolt_diameter)

        elif self.connection_type == 'end_plate':
            result = self._generate_end_plate(beam, column, bolt_diameter)

        elif self.connection_type == 'extended_end_plate':
            result = self._generate_extended_end_plate(beam, column, bolt_diameter)

        elif self.connection_type == 'reduced_beam_section':
            result = self._generate_rbs(beam, column, bolt_diameter)

        elif self.connection_type == 'wuf_w':
            result = self._generate_wuf_w(beam, column)

        else:
            result = self._generate_shear_tab(beam, column, bolt_diameter)

        plates = result.get('plates', [])
        bolts = result.get('bolts', [])
        welds = result.get('welds', [])
        stiffeners = result.get('stiffeners', [])

        # Calcular capacidades
        shear_capacity = self._calculate_shear_capacity(result, bolt_diameter, bolt_grade)
        moment_capacity = self._calculate_moment_capacity(result, beam) if 'moment' in self.connection_type or self.connection_type in ['end_plate', 'extended_end_plate', 'reduced_beam_section', 'wuf_w'] else 0

        # Calcular peso
        weight = self._calculate_weight(plates, stiffeners)

        # Resumen
        summary = {
            'connection_type': self.connection_type,
            'seismic_category': self.seismic_category,
            'beam_profile': beam_profile,
            'column_profile': column_profile,
            'bolt_diameter': bolt_diameter,
            'bolt_grade': bolt_grade,
            'bolt_count': len(bolts),
            'plate_count': len(plates),
            'stiffener_count': len(stiffeners),
            'shear_capacity': shear_capacity,
            'moment_capacity': moment_capacity,
            'weight': weight
        }

        return ConnectionData(
            type=self.connection_type,
            beam_profile=beam_profile,
            column_profile=column_profile,
            plates=plates,
            bolts=bolts,
            welds=welds,
            stiffeners=stiffeners,
            shear_capacity=shear_capacity,
            moment_capacity=moment_capacity,
            weight=weight,
            summary=summary
        )

    def _generate_shear_tab(self, beam, column, bolt_diameter):
        """Genera conexion shear tab."""
        # Numero de tornillos basado en altura de viga
        bolt_rows = self._calculate_bolt_rows(beam.d, bolt_diameter, 'shear')

        # Crear shear tab
        plate = self.plate_builder.create_shear_tab(
            beam, column, bolt_rows, bolt_diameter
        )

        # Crear tornillos
        edge_dist = self.plate_builder._get_edge_distance(bolt_diameter)
        spacing = bolt_diameter * 3

        bolt_center = rg.Point3d(
            column.bf / 2 + 10 + edge_dist,  # Posicion X
            0,
            beam.d / 2 - 25 - edge_dist - (bolt_rows - 1) * spacing / 2
        )

        grip = 10 + beam.tw + 10  # plate + web + washer
        bolts = self.bolt_builder.create_bolt_pattern(
            bolt_center, bolt_rows, 1, spacing, 0, grip
        )

        # Soldaduras
        welds = []
        weld_size = self.weld_builder.get_minimum_fillet_size(10)
        plate_height = 2 * edge_dist + (bolt_rows - 1) * spacing

        # Soldadura vertical en ambos lados
        weld_start = rg.Point3d(column.bf/2, -5, beam.d/2 - 25)
        weld_end = rg.Point3d(column.bf/2, -5, beam.d/2 - 25 - plate_height)
        welds.extend(self.weld_builder.create_fillet_weld_line(weld_start, weld_end, weld_size))

        return {
            'plates': [plate] if plate else [],
            'bolts': bolts,
            'welds': welds,
            'stiffeners': [],
            'bolt_rows': bolt_rows
        }

    def _generate_end_plate(self, beam, column, bolt_diameter):
        """Genera conexion end plate."""
        # Crear end plate flush
        plate = self.plate_builder.create_end_plate(beam, thickness=25)

        # Tornillos (4 en patines + 2-4 en alma)
        edge_dist = self.plate_builder._get_edge_distance(bolt_diameter)
        spacing = bolt_diameter * 3

        bolts = []
        grip = 25 + column.tf + 10  # plate + flange + washer

        # Tornillos en patin superior
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-25/2, y_offset, beam.d/2 - beam.tf/2)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Tornillos en patin inferior
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-25/2, y_offset, -beam.d/2 + beam.tf/2)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Rigidizadores de continuidad
        stiffeners = []
        cont_top = self.plate_builder.create_continuity_plate(column, beam, 'top')
        cont_bot = self.plate_builder.create_continuity_plate(column, beam, 'bottom')
        stiffeners.extend(cont_top)
        stiffeners.extend(cont_bot)

        # Soldaduras CJP en patines
        welds = []

        return {
            'plates': [plate] if plate else [],
            'bolts': bolts,
            'welds': welds,
            'stiffeners': stiffeners,
            'bolt_count': len(bolts)
        }

    def _generate_extended_end_plate(self, beam, column, bolt_diameter):
        """Genera conexion extended end plate."""
        # Extension tipica
        extension = 100  # mm arriba y abajo

        # Crear extended end plate
        plate = self.plate_builder.create_end_plate(
            beam, thickness=32,
            extended_top=extension,
            extended_bottom=extension
        )

        # Mas tornillos que flush end plate
        bolts = []
        edge_dist = self.plate_builder._get_edge_distance(bolt_diameter)
        grip = 32 + column.tf + 10

        # Tornillos en extension superior (2)
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-32/2, y_offset, beam.d/2 + extension/2)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Tornillos bajo patin superior (2)
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-32/2, y_offset, beam.d/2 - beam.tf - edge_dist)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Tornillos sobre patin inferior (2)
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-32/2, y_offset, -beam.d/2 + beam.tf + edge_dist)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Tornillos en extension inferior (2)
        for y_offset in [-beam.bf/4, beam.bf/4]:
            bolt_pos = rg.Point3d(-32/2, y_offset, -beam.d/2 - extension/2)
            bolt = self.bolt_builder.create_bolt(bolt_pos, grip)
            if bolt:
                bolts.append(bolt)

        # Rigidizadores
        stiffeners = []
        cont_top = self.plate_builder.create_continuity_plate(column, beam, 'top')
        cont_bot = self.plate_builder.create_continuity_plate(column, beam, 'bottom')
        stiffeners.extend(cont_top)
        stiffeners.extend(cont_bot)

        # Verificar si se requiere doubler plate
        # (simplificado: agregar si columna es "delgada")
        if column.tw < beam.tf:
            doubler = self.plate_builder.create_doubler_plate(column, beam)
            if doubler:
                stiffeners.append(doubler)

        return {
            'plates': [plate] if plate else [],
            'bolts': bolts,
            'welds': [],
            'stiffeners': stiffeners,
            'bolt_count': len(bolts)
        }

    def _generate_rbs(self, beam, column, bolt_diameter):
        """Genera conexion RBS (Reduced Beam Section)."""
        # Calcular corte RBS
        rbs_dims = self.rbs_builder.calculate_rbs_dimensions(beam)

        # Usar end plate para la conexion
        result = self._generate_end_plate(beam, column, bolt_diameter)

        # Agregar informacion de RBS
        result['rbs_dimensions'] = rbs_dims

        return result

    def _generate_wuf_w(self, beam, column):
        """Genera conexion WUF-W (Welded Unreinforced Flange - Welded Web)."""
        plates = []
        stiffeners = []
        welds = []

        # Shear tab para el alma
        bolt_rows = self._calculate_bolt_rows(beam.d, 22, 'shear')
        shear_tab = self.plate_builder.create_shear_tab(beam, column, bolt_rows, 22)
        if shear_tab:
            plates.append(shear_tab)

        # Rigidizadores de continuidad
        cont_top = self.plate_builder.create_continuity_plate(column, beam, 'top')
        cont_bot = self.plate_builder.create_continuity_plate(column, beam, 'bottom')
        stiffeners.extend(cont_top)
        stiffeners.extend(cont_bot)

        # Verificar doubler plate
        if column.tw < 0.9 * beam.tf:
            doubler = self.plate_builder.create_doubler_plate(column, beam)
            if doubler:
                stiffeners.append(doubler)

        # CJP welds en patines (representacion)
        # Top flange
        weld_start = rg.Point3d(0, -beam.bf/2, beam.d/2 - beam.tf/2)
        weld_end = rg.Point3d(0, beam.bf/2, beam.d/2 - beam.tf/2)
        welds.append(rg.Line(weld_start, weld_end).ToNurbsCurve())

        # Bottom flange
        weld_start = rg.Point3d(0, -beam.bf/2, -beam.d/2 + beam.tf/2)
        weld_end = rg.Point3d(0, beam.bf/2, -beam.d/2 + beam.tf/2)
        welds.append(rg.Line(weld_start, weld_end).ToNurbsCurve())

        return {
            'plates': plates,
            'bolts': [],
            'welds': welds,
            'stiffeners': stiffeners
        }

    def _calculate_bolt_rows(self, beam_depth, bolt_diameter, connection_type):
        """Calcula numero de filas de tornillos."""
        edge_dist = self.plate_builder._get_edge_distance(bolt_diameter)
        spacing = bolt_diameter * 3

        if connection_type == 'shear':
            # Altura disponible en alma
            available_height = beam_depth - 2 * 25  # Menos cope
            return max(2, min(6, int((available_height - 2 * edge_dist) / spacing) + 1))
        else:
            return 4

    def _calculate_shear_capacity(self, result, bolt_diameter, bolt_grade):
        """Calcula capacidad a corte (simplificado)."""
        bolt_count = len(result.get('bolts', []))

        # Capacidad por tornillo (kN)
        if bolt_grade == 'A325':
            Fnv = 372  # MPa (N threads)
        else:
            Fnv = 457  # A490

        Ab = math.pi * (bolt_diameter / 2) ** 2  # mm2
        phi_Rn = 0.75 * Fnv * Ab / 1000  # kN por tornillo

        return phi_Rn * bolt_count

    def _calculate_moment_capacity(self, result, beam):
        """Calcula capacidad a momento (simplificado)."""
        # Mp = Fy * Zx
        Fy = 345  # MPa (A992)
        Zx = beam.Zx * 1000  # mm3

        if self.connection_type == 'reduced_beam_section':
            rbs_dims = result.get('rbs_dimensions', {})
            Zrbs = rbs_dims.get('Zrbs', beam.Zx) * 1000
            return 0.9 * Fy * Zrbs / 1e6  # kN-m
        else:
            return 0.9 * Fy * Zx / 1e6  # kN-m

    def _calculate_weight(self, plates, stiffeners):
        """Calcula peso de la conexion."""
        # Estimacion simplificada
        weight = 0

        for plate in plates:
            if plate:
                props = rg.VolumeMassProperties.Compute(plate)
                if props:
                    volume = props.Volume / 1e9  # m3
                    weight += volume * 7850  # kg

        for stiff in stiffeners:
            if stiff:
                props = rg.VolumeMassProperties.Compute(stiff)
                if props:
                    volume = props.Volume / 1e9
                    weight += volume * 7850

        return weight


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    generator = ConnectionGenerator(
        connection_type=connection_type if 'connection_type' in dir() else 'shear_tab',
        seismic_category=seismic_category if 'seismic_category' in dir() else 'none'
    )

    result = generator.generate(
        beam_profile=beam_profile if 'beam_profile' in dir() else 'W18x50',
        column_profile=column_profile if 'column_profile' in dir() else 'W14x90',
        bolt_diameter=bolt_diameter if 'bolt_diameter' in dir() else 22,
        bolt_grade=bolt_grade if 'bolt_grade' in dir() else 'A325'
    )

    if result:
        # Salidas para Grasshopper
        plates = result.plates
        bolts = result.bolts
        welds = result.welds
        stiffeners = result.stiffeners
        shear_capacity = result.shear_capacity
        moment_capacity = result.moment_capacity
        weight = result.weight
        summary = result.summary
