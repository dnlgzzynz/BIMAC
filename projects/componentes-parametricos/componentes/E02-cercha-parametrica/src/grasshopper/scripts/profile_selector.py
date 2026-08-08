"""
Profile Selector - Cercha Parametrica
Selecciona y dimensiona perfiles estructurales para cada miembro.

Inputs:
    member_data (List[MemberData]): Datos de miembros
    forces (List[dict]): Fuerzas en cada miembro (opcional)
    material (str): Material de acero
    profile_type (str): Tipo de perfil preferido
    optimization_mode (str): Modo de optimizacion

Outputs:
    profiles (List[dict]): Perfil asignado a cada miembro
    sections (List[Brep]): Geometria 3D de perfiles
    weight_total (float): Peso total (kg)
    utilization (List[float]): Utilizacion de cada miembro
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos del perfil
ProfileData = namedtuple('ProfileData', [
    'name', 'type', 'dimensions', 'area', 'Ix', 'Iy',
    'rx', 'ry', 'weight', 'Zx', 'Zy'
])

# Resultado de seleccion
SelectionResult = namedtuple('SelectionResult', [
    'member_id', 'profile', 'length', 'weight',
    'slenderness', 'utilization', 'governing_mode'
])


class SteelProfiles:
    """Base de datos de perfiles de acero."""

    # HSS Cuadrados (mm, cm2, cm4, kg/m)
    HSS_PROFILES = {
        'HSS_50x50x3': ProfileData(
            'HSS 50x50x3', 'HSS', (50, 50, 3),
            5.41, 14.8, 14.8, 1.65, 1.65, 4.25, 5.92, 5.92
        ),
        'HSS_60x60x3': ProfileData(
            'HSS 60x60x3', 'HSS', (60, 60, 3),
            6.61, 26.1, 26.1, 1.99, 1.99, 5.19, 8.70, 8.70
        ),
        'HSS_75x75x3': ProfileData(
            'HSS 75x75x3', 'HSS', (75, 75, 3),
            8.41, 53.2, 53.2, 2.52, 2.52, 6.60, 14.2, 14.2
        ),
        'HSS_75x75x4': ProfileData(
            'HSS 75x75x4', 'HSS', (75, 75, 4),
            10.9, 66.5, 66.5, 2.47, 2.47, 8.56, 17.7, 17.7
        ),
        'HSS_100x100x4': ProfileData(
            'HSS 100x100x4', 'HSS', (100, 100, 4),
            14.4, 166, 166, 3.40, 3.40, 11.3, 33.2, 33.2
        ),
        'HSS_100x100x5': ProfileData(
            'HSS 100x100x5', 'HSS', (100, 100, 5),
            17.6, 197, 197, 3.34, 3.34, 13.8, 39.4, 39.4
        ),
        'HSS_100x100x6': ProfileData(
            'HSS 100x100x6', 'HSS', (100, 100, 6),
            20.9, 228, 228, 3.30, 3.30, 16.4, 45.6, 45.6
        ),
        'HSS_125x125x5': ProfileData(
            'HSS 125x125x5', 'HSS', (125, 125, 5),
            22.6, 396, 396, 4.19, 4.19, 17.7, 63.4, 63.4
        ),
        'HSS_125x125x6': ProfileData(
            'HSS 125x125x6', 'HSS', (125, 125, 6),
            26.6, 457, 457, 4.15, 4.15, 20.9, 73.1, 73.1
        ),
        'HSS_150x150x5': ProfileData(
            'HSS 150x150x5', 'HSS', (150, 150, 5),
            27.6, 698, 698, 5.03, 5.03, 21.7, 93.1, 93.1
        ),
        'HSS_150x150x6': ProfileData(
            'HSS 150x150x6', 'HSS', (150, 150, 6),
            32.9, 833, 833, 5.03, 5.03, 25.8, 111, 111
        ),
        'HSS_150x150x8': ProfileData(
            'HSS 150x150x8', 'HSS', (150, 150, 8),
            42.9, 1050, 1050, 4.95, 4.95, 33.7, 140, 140
        ),
        'HSS_175x175x6': ProfileData(
            'HSS 175x175x6', 'HSS', (175, 175, 6),
            38.9, 1340, 1340, 5.87, 5.87, 30.5, 153, 153
        ),
        'HSS_175x175x8': ProfileData(
            'HSS 175x175x8', 'HSS', (175, 175, 8),
            50.9, 1710, 1710, 5.80, 5.80, 40.0, 195, 195
        ),
        'HSS_200x200x6': ProfileData(
            'HSS 200x200x6', 'HSS', (200, 200, 6),
            44.9, 2020, 2020, 6.71, 6.71, 35.2, 202, 202
        ),
        'HSS_200x200x8': ProfileData(
            'HSS 200x200x8', 'HSS', (200, 200, 8),
            58.1, 2560, 2560, 6.64, 6.64, 45.6, 256, 256
        ),
        'HSS_200x200x10': ProfileData(
            'HSS 200x200x10', 'HSS', (200, 200, 10),
            71.4, 3050, 3050, 6.54, 6.54, 56.1, 305, 305
        ),
        'HSS_250x250x8': ProfileData(
            'HSS 250x250x8', 'HSS', (250, 250, 8),
            73.6, 5160, 5160, 8.37, 8.37, 57.8, 413, 413
        ),
        'HSS_250x250x10': ProfileData(
            'HSS 250x250x10', 'HSS', (250, 250, 10),
            90.9, 6180, 6180, 8.25, 8.25, 71.4, 494, 494
        ),
        'HSS_300x300x10': ProfileData(
            'HSS 300x300x10', 'HSS', (300, 300, 10),
            110, 10900, 10900, 9.95, 9.95, 86.3, 727, 727
        ),
    }

    # Angulos (mm, cm2, cm4, kg/m)
    ANGLE_PROFILES = {
        'L_40x40x4': ProfileData(
            'L 40x40x4', 'L', (40, 40, 4),
            3.08, 4.47, 4.47, 1.20, 1.20, 2.42, 1.57, 1.57
        ),
        'L_50x50x5': ProfileData(
            'L 50x50x5', 'L', (50, 50, 5),
            4.80, 11.0, 11.0, 1.51, 1.51, 3.77, 3.08, 3.08
        ),
        'L_60x60x6': ProfileData(
            'L 60x60x6', 'L', (60, 60, 6),
            6.91, 22.8, 22.8, 1.82, 1.82, 5.42, 5.32, 5.32
        ),
        'L_75x75x6': ProfileData(
            'L 75x75x6', 'L', (75, 75, 6),
            8.73, 51.7, 51.7, 2.43, 2.43, 6.85, 9.66, 9.66
        ),
        'L_75x75x8': ProfileData(
            'L 75x75x8', 'L', (75, 75, 8),
            11.4, 65.5, 65.5, 2.40, 2.40, 8.95, 12.2, 12.2
        ),
        'L_100x100x8': ProfileData(
            'L 100x100x8', 'L', (100, 100, 8),
            15.5, 166, 166, 3.27, 3.27, 12.2, 23.2, 23.2
        ),
        'L_100x100x10': ProfileData(
            'L 100x100x10', 'L', (100, 100, 10),
            19.2, 200, 200, 3.23, 3.23, 15.1, 28.0, 28.0
        ),
    }

    # Tubos redondos (diametro, espesor, cm2, cm4, kg/m)
    PIPE_PROFILES = {
        'PIPE_48x3': ProfileData(
            'PIPE 48.3x3.2', 'PIPE', (48.3, 3.2),
            4.53, 11.6, 11.6, 1.60, 1.60, 3.56, 4.80, 4.80
        ),
        'PIPE_60x4': ProfileData(
            'PIPE 60.3x4', 'PIPE', (60.3, 4.0),
            7.03, 28.3, 28.3, 2.01, 2.01, 5.52, 9.38, 9.38
        ),
        'PIPE_76x5': ProfileData(
            'PIPE 76.1x5', 'PIPE', (76.1, 5.0),
            11.2, 70.9, 70.9, 2.52, 2.52, 8.79, 18.6, 18.6
        ),
        'PIPE_89x5': ProfileData(
            'PIPE 89x5', 'PIPE', (89, 5.0),
            13.2, 116, 116, 2.97, 2.97, 10.4, 26.1, 26.1
        ),
        'PIPE_114x6': ProfileData(
            'PIPE 114.3x6', 'PIPE', (114.3, 6.0),
            20.4, 289, 289, 3.77, 3.77, 16.0, 50.6, 50.6
        ),
        'PIPE_139x6': ProfileData(
            'PIPE 139.7x6', 'PIPE', (139.7, 6.0),
            25.2, 530, 530, 4.59, 4.59, 19.8, 75.9, 75.9
        ),
        'PIPE_168x8': ProfileData(
            'PIPE 168.3x8', 'PIPE', (168.3, 8.0),
            40.3, 1200, 1200, 5.46, 5.46, 31.6, 143, 143
        ),
    }

    @classmethod
    def get_all_profiles(cls, profile_type=None):
        """Obtiene todos los perfiles de un tipo."""
        if profile_type == 'HSS':
            return cls.HSS_PROFILES
        elif profile_type == 'L':
            return cls.ANGLE_PROFILES
        elif profile_type == 'PIPE':
            return cls.PIPE_PROFILES
        else:
            # Todos los perfiles
            all_profiles = {}
            all_profiles.update(cls.HSS_PROFILES)
            all_profiles.update(cls.ANGLE_PROFILES)
            all_profiles.update(cls.PIPE_PROFILES)
            return all_profiles

    @classmethod
    def get_profile(cls, name):
        """Obtiene un perfil por nombre."""
        all_profiles = cls.get_all_profiles()
        return all_profiles.get(name)


class SteelMaterials:
    """Propiedades de materiales de acero."""

    MATERIALS = {
        'A36': {
            'Fy': 250,      # MPa
            'Fu': 400,      # MPa
            'E': 200000,    # MPa
            'G': 77200,     # MPa
            'density': 7850  # kg/m3
        },
        'A572_Gr50': {
            'Fy': 345,
            'Fu': 450,
            'E': 200000,
            'G': 77200,
            'density': 7850
        },
        'A500_Gr_B': {
            'Fy': 290,
            'Fu': 400,
            'E': 200000,
            'G': 77200,
            'density': 7850
        },
        'A500_Gr_C': {
            'Fy': 317,
            'Fu': 427,
            'E': 200000,
            'G': 77200,
            'density': 7850
        },
    }

    @classmethod
    def get_material(cls, name):
        """Obtiene propiedades del material."""
        return cls.MATERIALS.get(name, cls.MATERIALS['A500_Gr_B'])


class ProfileSelector:
    """Selector de perfiles para miembros de cercha."""

    def __init__(self, material='A500_Gr_B'):
        """
        Args:
            material: Nombre del material de acero
        """
        self.material = SteelMaterials.get_material(material)
        self.Fy = self.material['Fy']
        self.E = self.material['E']
        self.phi_c = 0.90  # Factor de resistencia compresion
        self.phi_t = 0.90  # Factor de resistencia tension

    def select_profiles(self, member_data, forces=None,
                        profile_type='HSS', optimization_mode='weight'):
        """
        Selecciona perfiles para todos los miembros.

        Args:
            member_data: Lista de MemberData
            forces: Fuerzas en cada miembro (kN)
            profile_type: Tipo de perfil preferido
            optimization_mode: 'weight' o 'cost'

        Returns:
            List[SelectionResult]
        """
        results = []
        profiles = SteelProfiles.get_all_profiles(profile_type)

        for i, member in enumerate(member_data):
            # Obtener fuerza si esta disponible
            if forces and i < len(forces):
                force = forces[i]
            else:
                # Estimar fuerza basada en tipologia
                force = self._estimate_force(member)

            # Seleccionar perfil
            result = self._select_for_member(
                member, force, profiles, optimization_mode
            )
            results.append(result)

        return results

    def _estimate_force(self, member):
        """Estima fuerza basada en tipo de miembro."""
        # Estimaciones tipicas para cercha de 12m de luz
        # con carga de 1 kN/m2
        length_m = member.length / 1000.0

        if member.type.value == 'top_chord':
            return -50 * length_m  # Compresion (kN)
        elif member.type.value == 'bottom_chord':
            return 45 * length_m   # Tension (kN)
        elif member.type.value == 'diagonal':
            return -25 * length_m  # Compresion tipica
        else:  # vertical
            return -15 * length_m  # Compresion menor

    def _select_for_member(self, member, force, profiles, optimization_mode):
        """Selecciona el perfil optimo para un miembro."""
        length_mm = member.length
        is_compression = force < 0 if force else True

        # Filtrar y ordenar perfiles por peso
        sorted_profiles = sorted(
            profiles.values(),
            key=lambda p: p.weight
        )

        best_profile = None
        best_utilization = 0
        governing_mode = None

        for profile in sorted_profiles:
            # Verificar capacidad
            if is_compression:
                capacity, mode = self._compression_capacity(
                    profile, length_mm
                )
            else:
                capacity, mode = self._tension_capacity(profile)

            # Calcular utilizacion
            utilization = abs(force) / capacity if capacity > 0 else float('inf')

            # Si cumple y es el mas ligero hasta ahora
            if utilization <= 1.0:
                if best_profile is None or profile.weight < best_profile.weight:
                    best_profile = profile
                    best_utilization = utilization
                    governing_mode = mode
                    break  # Tomar el primero que cumple (mas ligero)

        # Si ningun perfil cumple, tomar el mas grande
        if best_profile is None:
            best_profile = sorted_profiles[-1]
            if is_compression:
                capacity, governing_mode = self._compression_capacity(
                    best_profile, length_mm
                )
            else:
                capacity, governing_mode = self._tension_capacity(best_profile)
            best_utilization = abs(force) / capacity if capacity > 0 else 1.5

        # Calcular esbeltez
        r_min = min(best_profile.rx, best_profile.ry) * 10  # cm a mm
        slenderness = length_mm / r_min if r_min > 0 else 999

        # Peso del miembro
        weight = best_profile.weight * (length_mm / 1000.0)

        return SelectionResult(
            member_id=member.id,
            profile=best_profile,
            length=length_mm,
            weight=weight,
            slenderness=slenderness,
            utilization=best_utilization,
            governing_mode=governing_mode
        )

    def _compression_capacity(self, profile, length_mm):
        """
        Calcula capacidad a compresion segun AISC.

        Returns:
            tuple: (capacidad_kN, modo_gobernante)
        """
        # Propiedades
        A = profile.area * 100  # cm2 a mm2
        r_min = min(profile.rx, profile.ry) * 10  # cm a mm

        # Esbeltez
        K = 1.0  # Factor de longitud efectiva
        Lc = K * length_mm
        slenderness = Lc / r_min if r_min > 0 else 999

        # Esbeltez limite
        Fe = (math.pi ** 2 * self.E) / (slenderness ** 2) if slenderness > 0 else self.Fy

        # Esfuerzo critico segun AISC E3
        if slenderness <= 4.71 * math.sqrt(self.E / self.Fy):
            # Pandeo inelastico
            Fcr = (0.658 ** (self.Fy / Fe)) * self.Fy
            mode = 'inelastic_buckling'
        else:
            # Pandeo elastico
            Fcr = 0.877 * Fe
            mode = 'elastic_buckling'

        # Capacidad nominal
        Pn = Fcr * A / 1000  # N a kN

        # Capacidad de diseno
        Pc = self.phi_c * Pn

        return Pc, mode

    def _tension_capacity(self, profile):
        """
        Calcula capacidad a tension segun AISC.

        Returns:
            tuple: (capacidad_kN, modo_gobernante)
        """
        A = profile.area * 100  # cm2 a mm2

        # Fluencia en seccion bruta
        Pn_yield = self.Fy * A / 1000  # kN

        # Capacidad de diseno
        Pt = self.phi_t * Pn_yield

        return Pt, 'yielding'

    def calculate_total_weight(self, results):
        """Calcula peso total de la cercha."""
        return sum(r.weight for r in results)

    def get_profile_summary(self, results):
        """Genera resumen de perfiles utilizados."""
        profile_counts = {}
        profile_lengths = {}

        for r in results:
            name = r.profile.name
            if name not in profile_counts:
                profile_counts[name] = 0
                profile_lengths[name] = 0

            profile_counts[name] += 1
            profile_lengths[name] += r.length

        return {
            'counts': profile_counts,
            'lengths': profile_lengths,
            'unique_profiles': len(profile_counts)
        }


class ProfileGeometryBuilder:
    """Construye geometria 3D de los perfiles."""

    def __init__(self):
        self.tolerance = 0.001

    def build_member_geometry(self, member, profile):
        """
        Construye la geometria 3D de un miembro.

        Args:
            member: MemberData
            profile: ProfileData

        Returns:
            Brep: Geometria del perfil
        """
        line = member.line

        # Crear seccion del perfil
        section = self._create_section(profile)
        if section is None:
            return None

        # Obtener frame al inicio
        start_point = line.From
        direction = line.Direction
        direction.Unitize()

        # Crear plano perpendicular
        plane = rg.Plane(start_point, direction)

        # Transformar seccion al plano
        xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, plane)
        section.Transform(xform)

        # Extruir
        extrusion = rg.Extrusion.Create(section, member.length, True)
        if extrusion:
            return extrusion.ToBrep()

        return None

    def _create_section(self, profile):
        """Crea la curva de seccion del perfil."""
        if profile.type == 'HSS':
            return self._create_hss_section(profile)
        elif profile.type == 'L':
            return self._create_angle_section(profile)
        elif profile.type == 'PIPE':
            return self._create_pipe_section(profile)
        return None

    def _create_hss_section(self, profile):
        """Crea seccion HSS (rectangular hueca)."""
        b, h, t = profile.dimensions
        b = b / 2  # Mitad para centrar
        h = h / 2

        # Rectangulo exterior
        outer = rg.Rectangle3d(
            rg.Plane.WorldXY,
            rg.Interval(-b, b),
            rg.Interval(-h, h)
        )

        return outer.ToNurbsCurve()

    def _create_angle_section(self, profile):
        """Crea seccion de angulo."""
        b, h, t = profile.dimensions

        points = [
            rg.Point3d(0, 0, 0),
            rg.Point3d(b, 0, 0),
            rg.Point3d(b, t, 0),
            rg.Point3d(t, t, 0),
            rg.Point3d(t, h, 0),
            rg.Point3d(0, h, 0),
            rg.Point3d(0, 0, 0)
        ]

        polyline = rg.Polyline(points)
        return polyline.ToNurbsCurve()

    def _create_pipe_section(self, profile):
        """Crea seccion de tubo circular."""
        d, t = profile.dimensions
        r = d / 2

        circle = rg.Circle(rg.Plane.WorldXY, r)
        return circle.ToNurbsCurve()


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    selector = ProfileSelector(
        material=material if 'material' in dir() else 'A500_Gr_B'
    )

    results = selector.select_profiles(
        member_data=member_data if 'member_data' in dir() else [],
        forces=forces if 'forces' in dir() else None,
        profile_type=profile_type if 'profile_type' in dir() else 'HSS',
        optimization_mode=optimization_mode if 'optimization_mode' in dir() else 'weight'
    )

    # Construir geometria
    builder = ProfileGeometryBuilder()
    sections = []
    for i, result in enumerate(results):
        if i < len(member_data):
            geom = builder.build_member_geometry(member_data[i], result.profile)
            sections.append(geom)

    # Salidas para Grasshopper
    profiles = [r.profile for r in results]
    weight_total = selector.calculate_total_weight(results)
    utilization = [r.utilization for r in results]
    summary = selector.get_profile_summary(results)
