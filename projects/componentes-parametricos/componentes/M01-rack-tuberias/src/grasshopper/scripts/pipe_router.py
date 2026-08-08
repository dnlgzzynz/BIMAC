"""
Pipe Router - Rack de Tuberias Parametrico
Genera ruteo de tuberias sobre la estructura del rack.

Inputs:
    rack_data (RackData): Datos de la estructura del rack
    pipe_schedule (List[dict]): Lista de tuberias
    routing_options (dict): Opciones de ruteo

Outputs:
    pipes (List[Brep]): Geometria de tuberias
    insulation (List[Brep]): Geometria de aislamiento
    fittings (List[Brep]): Accesorios (codos, tees)
    pipe_data (List[dict]): Datos de cada tuberia
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Datos de tuberia
PipeData = namedtuple('PipeData', [
    'id', 'size', 'schedule', 'material', 'service',
    'length', 'weight', 'insulation_type', 'tier',
    'centerline', 'brep'
])

# Resultado del ruteo
RoutingResult = namedtuple('RoutingResult', [
    'pipes', 'insulation', 'fittings', 'centerlines',
    'pipe_data', 'total_length', 'total_weight', 'summary'
])

# Dimensiones de tuberia por NPS (mm)
PIPE_DIMENSIONS = {
    # NPS: {OD, wall_sch40, wall_sch80, ID_sch40}
    0.5: {'OD': 21.3, 'wall_40': 2.77, 'wall_80': 3.73},
    0.75: {'OD': 26.7, 'wall_40': 2.87, 'wall_80': 3.91},
    1: {'OD': 33.4, 'wall_40': 3.38, 'wall_80': 4.55},
    1.5: {'OD': 48.3, 'wall_40': 3.68, 'wall_80': 5.08},
    2: {'OD': 60.3, 'wall_40': 3.91, 'wall_80': 5.54},
    3: {'OD': 88.9, 'wall_40': 5.49, 'wall_80': 7.62},
    4: {'OD': 114.3, 'wall_40': 6.02, 'wall_80': 8.56},
    6: {'OD': 168.3, 'wall_40': 7.11, 'wall_80': 10.97},
    8: {'OD': 219.1, 'wall_40': 8.18, 'wall_80': 12.70},
    10: {'OD': 273.0, 'wall_40': 9.27, 'wall_80': 15.09},
    12: {'OD': 323.8, 'wall_40': 10.31, 'wall_80': 17.48},
    14: {'OD': 355.6, 'wall_40': 11.13, 'wall_80': 19.05},
    16: {'OD': 406.4, 'wall_40': 12.70, 'wall_80': 21.44},
    18: {'OD': 457.2, 'wall_40': 14.27, 'wall_80': 23.83},
    20: {'OD': 508.0, 'wall_40': 15.09, 'wall_80': 26.19},
    24: {'OD': 609.6, 'wall_40': 17.48, 'wall_80': 30.96},
}

# Peso de tuberia por metro (kg/m) - Sch 40 con agua
PIPE_WEIGHT = {
    2: {'empty': 5.4, 'water': 8.2},
    3: {'empty': 11.3, 'water': 18.4},
    4: {'empty': 16.1, 'water': 28.3},
    6: {'empty': 28.3, 'water': 56.7},
    8: {'empty': 43.8, 'water': 94.6},
    10: {'empty': 60.3, 'water': 140.2},
    12: {'empty': 77.0, 'water': 190.0},
    14: {'empty': 106.0, 'water': 261.0},
    16: {'empty': 136.0, 'water': 349.0},
    18: {'empty': 170.0, 'water': 453.0},
    20: {'empty': 206.0, 'water': 571.0},
    24: {'empty': 283.0, 'water': 844.0},
}

# Espesor de aislamiento por servicio y temperatura
INSULATION_THICKNESS = {
    'cold_water': {2: 25, 4: 38, 6: 50, 8: 50, 10: 63, 12: 63},
    'hot_water': {2: 38, 4: 50, 6: 63, 8: 75, 10: 75, 12: 88},
    'steam_low': {2: 50, 4: 63, 6: 75, 8: 88, 10: 100, 12: 100},
    'steam_high': {2: 75, 4: 88, 6: 100, 8: 113, 10: 125, 12: 125},
    'chilled': {2: 50, 4: 63, 6: 75, 8: 88, 10: 100, 12: 100},
    'process': {2: 38, 4: 50, 6: 63, 8: 75, 10: 88, 12: 88},
}


class PipeGeometryBuilder:
    """Construye geometria de tuberias."""

    def __init__(self, schedule='40'):
        self.schedule = schedule

    def get_dimensions(self, nps):
        """Obtiene dimensiones de tuberia."""
        if nps in PIPE_DIMENSIONS:
            dims = PIPE_DIMENSIONS[nps]
            wall_key = f'wall_{self.schedule}'
            wall = dims.get(wall_key, dims['wall_40'])
            return {
                'OD': dims['OD'],
                'wall': wall,
                'ID': dims['OD'] - 2 * wall
            }
        return {'OD': 60.3, 'wall': 3.91, 'ID': 52.5}  # Default 2"

    def create_pipe_segment(self, start_point, end_point, nps):
        """
        Crea un segmento de tuberia.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            nps: Tamano nominal (pulgadas)

        Returns:
            Brep: Geometria de la tuberia
        """
        dims = self.get_dimensions(nps)
        radius = dims['OD'] / 2

        # Crear linea central
        centerline = rg.Line(start_point, end_point)

        # Crear tuberia como pipe
        pipes = rg.Brep.CreatePipe(
            centerline.ToNurbsCurve(),
            radius,
            False,  # Local blending
            rg.PipeCapMode.Flat,
            True,   # Fit rail
            0.01,   # Abs tolerance
            0.01    # Angle tolerance
        )

        if pipes and len(pipes) > 0:
            return pipes[0]
        return None

    def create_pipe_from_curve(self, curve, nps):
        """
        Crea tuberia siguiendo una curva.

        Args:
            curve: Curva central
            nps: Tamano nominal

        Returns:
            Brep: Geometria de la tuberia
        """
        dims = self.get_dimensions(nps)
        radius = dims['OD'] / 2

        pipes = rg.Brep.CreatePipe(
            curve,
            radius,
            False,
            rg.PipeCapMode.Flat,
            True,
            0.01,
            0.01
        )

        if pipes and len(pipes) > 0:
            return pipes[0]
        return None

    def create_elbow(self, center, nps, radius_factor=1.5, start_angle=0, sweep_angle=90):
        """
        Crea un codo de tuberia.

        Args:
            center: Centro del arco
            nps: Tamano nominal
            radius_factor: Factor del radio de curvatura (1.5D, 3D, etc)
            start_angle: Angulo inicial (grados)
            sweep_angle: Angulo de barrido (grados)

        Returns:
            Brep: Geometria del codo
        """
        dims = self.get_dimensions(nps)
        pipe_radius = dims['OD'] / 2
        bend_radius = dims['OD'] * radius_factor

        # Crear arco
        arc = rg.Arc(
            rg.Plane(center, rg.Vector3d.ZAxis),
            bend_radius,
            math.radians(sweep_angle)
        )

        # Rotar al angulo inicial
        arc.Transform(rg.Transform.Rotation(
            math.radians(start_angle),
            rg.Vector3d.ZAxis,
            center
        ))

        # Crear pipe
        pipes = rg.Brep.CreatePipe(
            arc.ToNurbsCurve(),
            pipe_radius,
            False,
            rg.PipeCapMode.Flat,
            True,
            0.01,
            0.01
        )

        if pipes and len(pipes) > 0:
            return pipes[0]
        return None


class InsulationBuilder:
    """Construye aislamiento de tuberias."""

    def __init__(self):
        self.insulation_types = INSULATION_THICKNESS

    def get_thickness(self, nps, service):
        """Obtiene espesor de aislamiento."""
        thicknesses = self.insulation_types.get(service, self.insulation_types['process'])

        sizes = sorted(thicknesses.keys())
        for s in sizes:
            if nps <= s:
                return thicknesses[s]

        return thicknesses[max(sizes)]

    def create_insulation(self, pipe_brep, nps, service, cladding_thickness=0.5):
        """
        Crea aislamiento sobre una tuberia.

        Args:
            pipe_brep: Brep de la tuberia
            nps: Tamano nominal
            service: Tipo de servicio
            cladding_thickness: Espesor de recubrimiento (mm)

        Returns:
            Brep: Geometria del aislamiento
        """
        insulation_thickness = self.get_thickness(nps, service)

        if pipe_brep is None:
            return None

        # Offset del brep hacia afuera
        offset_breps = rg.Brep.CreateOffsetBrep(
            pipe_brep,
            insulation_thickness + cladding_thickness,
            True,  # Solid
            True,  # Both sides
            0.01   # Tolerance
        )

        if offset_breps and len(offset_breps) > 0:
            return offset_breps[0]
        return None

    def create_insulation_from_curve(self, curve, nps, service):
        """
        Crea aislamiento siguiendo una curva.

        Args:
            curve: Curva central
            nps: Tamano nominal
            service: Tipo de servicio

        Returns:
            Brep: Geometria del aislamiento
        """
        dims = PIPE_DIMENSIONS.get(nps, PIPE_DIMENSIONS[6])
        pipe_od = dims['OD']
        insulation_thickness = self.get_thickness(nps, service)
        total_radius = pipe_od / 2 + insulation_thickness

        pipes = rg.Brep.CreatePipe(
            curve,
            total_radius,
            False,
            rg.PipeCapMode.Flat,
            True,
            0.01,
            0.01
        )

        if pipes and len(pipes) > 0:
            return pipes[0]
        return None


class PipeRouter:
    """Enrutador de tuberias sobre el rack."""

    def __init__(self):
        self.pipe_builder = PipeGeometryBuilder()
        self.insulation_builder = InsulationBuilder()

    def route(self, rack_data, pipe_schedule, include_insulation=True,
              offset_start=500, pipe_gap=150):
        """
        Genera ruteo de tuberias sobre el rack.

        Args:
            rack_data: Datos del rack
            pipe_schedule: Lista de tuberias
            include_insulation: Incluir aislamiento
            offset_start: Offset desde inicio del rack (mm)
            pipe_gap: Separacion entre tuberias (mm)

        Returns:
            RoutingResult
        """
        all_pipes = []
        all_insulation = []
        all_fittings = []
        all_centerlines = []
        pipe_data_list = []

        summary = rack_data.summary
        total_length = summary['total_length']
        width = summary['width']
        tier_heights = summary['tier_heights']

        total_pipe_length = 0
        total_weight = 0

        # Procesar cada linea del schedule
        for idx, pipe_info in enumerate(pipe_schedule):
            nps = pipe_info.get('size', 6)
            count = pipe_info.get('count', 1)
            service = pipe_info.get('service', 'process')
            tier = pipe_info.get('tier', 0)
            material = pipe_info.get('material', 'carbon_steel')
            schedule = pipe_info.get('schedule', '40')
            has_insulation = pipe_info.get('insulated', True)

            if tier >= len(tier_heights):
                tier = len(tier_heights) - 1

            tier_height = tier_heights[tier]
            dims = self.pipe_builder.get_dimensions(nps)
            pipe_od = dims['OD']

            # Calcular espesor de aislamiento
            ins_thickness = 0
            if has_insulation and include_insulation:
                ins_thickness = self.insulation_builder.get_thickness(nps, service)

            # Altura de soporte (sobre el nivel)
            support_height = 100  # mm tipico para zapata

            for i in range(count):
                # Calcular posicion Y
                y_offset = -width/2 + 200 + i * (pipe_od + 2 * ins_thickness + pipe_gap)

                # Altura Z (centro de tuberia)
                z_pos = tier_height + support_height + pipe_od/2

                # Puntos de la tuberia
                start_pt = rg.Point3d(offset_start, y_offset, z_pos)
                end_pt = rg.Point3d(total_length - offset_start, y_offset, z_pos)

                # Crear linea central
                centerline = rg.Line(start_pt, end_pt)
                all_centerlines.append(centerline.ToNurbsCurve())

                # Crear tuberia
                pipe_brep = self.pipe_builder.create_pipe_segment(
                    start_pt, end_pt, nps
                )

                if pipe_brep:
                    all_pipes.append(pipe_brep)

                    # Calcular longitud y peso
                    pipe_length = start_pt.DistanceTo(end_pt) / 1000  # m
                    total_pipe_length += pipe_length

                    weight_data = PIPE_WEIGHT.get(int(nps), PIPE_WEIGHT[6])
                    weight = pipe_length * weight_data['water']
                    total_weight += weight

                    # Crear aislamiento
                    if has_insulation and include_insulation:
                        ins_brep = self.insulation_builder.create_insulation_from_curve(
                            centerline.ToNurbsCurve(), nps, service
                        )
                        if ins_brep:
                            all_insulation.append(ins_brep)

                    # Datos de la tuberia
                    pipe_data_list.append(PipeData(
                        id=f"PIPE-{len(pipe_data_list)+1:03d}",
                        size=nps,
                        schedule=schedule,
                        material=material,
                        service=service,
                        length=pipe_length * 1000,  # mm
                        weight=weight,
                        insulation_type=service if has_insulation else None,
                        tier=tier,
                        centerline=centerline.ToNurbsCurve(),
                        brep=pipe_brep
                    ))

        # Resumen
        result_summary = {
            'pipe_count': len(all_pipes),
            'insulation_count': len(all_insulation),
            'fitting_count': len(all_fittings),
            'total_length': total_pipe_length * 1000,  # mm
            'total_weight': total_weight,
            'pipe_schedule': pipe_schedule,
            'tiers_used': list(set(p.tier for p in pipe_data_list))
        }

        return RoutingResult(
            pipes=all_pipes,
            insulation=all_insulation,
            fittings=all_fittings,
            centerlines=all_centerlines,
            pipe_data=pipe_data_list,
            total_length=total_pipe_length * 1000,
            total_weight=total_weight,
            summary=result_summary
        )

    def route_with_drops(self, rack_data, pipe_schedule, drop_positions,
                          drop_height=1000):
        """
        Genera ruteo con bajadas verticales.

        Args:
            rack_data: Datos del rack
            pipe_schedule: Lista de tuberias
            drop_positions: Posiciones X de bajadas
            drop_height: Altura de bajada (mm)

        Returns:
            RoutingResult (extendido con bajadas)
        """
        # Primero generar ruteo horizontal normal
        result = self.route(rack_data, pipe_schedule)

        # Agregar bajadas
        drops = []
        drop_elbows = []

        for pipe_data in result.pipe_data:
            nps = pipe_data.size

            for drop_x in drop_positions:
                # Verificar si la bajada esta dentro del rango de la tuberia
                centerline = pipe_data.centerline
                start_x = centerline.PointAtStart.X
                end_x = centerline.PointAtEnd.X

                if start_x <= drop_x <= end_x:
                    # Obtener punto en la linea
                    t = (drop_x - start_x) / (end_x - start_x)
                    drop_point = centerline.PointAt(t * centerline.Domain.Length)

                    # Crear bajada vertical
                    drop_start = drop_point
                    drop_end = rg.Point3d(drop_point.X, drop_point.Y, drop_point.Z - drop_height)

                    drop_pipe = self.pipe_builder.create_pipe_segment(
                        drop_start, drop_end, nps
                    )

                    if drop_pipe:
                        drops.append(drop_pipe)

                    # Codo superior
                    elbow = self.pipe_builder.create_elbow(
                        drop_start, nps, 1.5, 0, 90
                    )
                    if elbow:
                        drop_elbows.append(elbow)

        # Agregar drops a los resultados
        all_pipes = list(result.pipes) + drops
        all_fittings = list(result.fittings) + drop_elbows

        return RoutingResult(
            pipes=all_pipes,
            insulation=result.insulation,
            fittings=all_fittings,
            centerlines=result.centerlines,
            pipe_data=result.pipe_data,
            total_length=result.total_length,
            total_weight=result.total_weight,
            summary=result.summary
        )


class PipeScheduleGenerator:
    """Genera schedules de tuberia tipicos."""

    @staticmethod
    def create_process_schedule(tier_count=3):
        """Crea schedule tipico de planta de proceso."""
        schedule = []

        # Nivel 0: Tuberias grandes de proceso
        schedule.extend([
            {'size': 12, 'count': 2, 'service': 'process', 'tier': 0, 'insulated': True},
            {'size': 8, 'count': 3, 'service': 'process', 'tier': 0, 'insulated': True},
        ])

        # Nivel 1: Servicios
        if tier_count > 1:
            schedule.extend([
                {'size': 6, 'count': 2, 'service': 'steam_low', 'tier': 1, 'insulated': True},
                {'size': 4, 'count': 3, 'service': 'hot_water', 'tier': 1, 'insulated': True},
                {'size': 3, 'count': 2, 'service': 'cold_water', 'tier': 1, 'insulated': True},
            ])

        # Nivel 2: Instrumentacion y aire
        if tier_count > 2:
            schedule.extend([
                {'size': 2, 'count': 4, 'service': 'process', 'tier': 2, 'insulated': False},
                {'size': 1, 'count': 6, 'service': 'process', 'tier': 2, 'insulated': False},
            ])

        return schedule

    @staticmethod
    def create_utility_schedule(tier_count=2):
        """Crea schedule de servicios/utilidades."""
        schedule = [
            {'size': 8, 'count': 1, 'service': 'cold_water', 'tier': 0, 'insulated': True},
            {'size': 6, 'count': 1, 'service': 'hot_water', 'tier': 0, 'insulated': True},
            {'size': 4, 'count': 2, 'service': 'steam_low', 'tier': 0, 'insulated': True},
            {'size': 3, 'count': 2, 'service': 'chilled', 'tier': 1, 'insulated': True},
            {'size': 2, 'count': 4, 'service': 'process', 'tier': 1, 'insulated': False},
        ]
        return schedule


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    router = PipeRouter()

    # Schedule por defecto
    default_schedule = PipeScheduleGenerator.create_process_schedule(
        tier_count=tier_count if 'tier_count' in dir() else 3
    )

    result = router.route(
        rack_data=rack_data if 'rack_data' in dir() else None,
        pipe_schedule=pipe_schedule if 'pipe_schedule' in dir() else default_schedule,
        include_insulation=include_insulation if 'include_insulation' in dir() else True,
        offset_start=offset_start if 'offset_start' in dir() else 500,
        pipe_gap=pipe_gap if 'pipe_gap' in dir() else 150
    )

    # Salidas para Grasshopper
    pipes = result.pipes
    insulation = result.insulation
    fittings = result.fittings
    centerlines = result.centerlines
    pipe_data = result.pipe_data
    total_length = result.total_length
    total_weight = result.total_weight
    summary = result.summary
