#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de Ductos - M02 Sistema HVAC Modular

Genera geometria de ductos rectangulares y circulares
con transiciones, codos y conexiones.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
DuctSegment = namedtuple('DuctSegment', [
    'brep', 'centerline', 'start_size', 'end_size',
    'length', 'type', 'cfm', 'velocity'
])

DuctFitting = namedtuple('DuctFitting', [
    'brep', 'type', 'size', 'angle', 'loss_coefficient'
])

DuctRun = namedtuple('DuctRun', [
    'segments', 'fittings', 'total_length', 'total_area',
    'pressure_drop', 'cfm'
])


class DuctSizer:
    """Calcula dimensiones de ductos basado en CFM y velocidad."""

    # Diametros circulares estandar (mm)
    CIRCULAR_SIZES = [100, 125, 150, 200, 250, 300, 350, 400,
                      450, 500, 600, 700, 800, 900, 1000]

    # Dimensiones rectangulares estandar (mm)
    RECTANGULAR_WIDTHS = [150, 200, 250, 300, 400, 500, 600,
                          750, 900, 1000, 1200, 1500, 1800, 2000]
    RECTANGULAR_HEIGHTS = [150, 200, 250, 300, 400, 500, 600, 750, 900, 1000]

    def __init__(self, max_aspect_ratio=4.0, velocity_limit=10.0):
        """
        Args:
            max_aspect_ratio: Relacion de aspecto maxima W/H
            velocity_limit: Velocidad maxima (m/s)
        """
        self.max_aspect = max_aspect_ratio
        self.velocity_limit = velocity_limit

    def cfm_to_cms(self, cfm):
        """Convierte CFM a m³/s."""
        return cfm * 0.000471947

    def size_circular(self, cfm, target_velocity):
        """
        Calcula diametro de ducto circular.

        Args:
            cfm: Flujo en CFM
            target_velocity: Velocidad deseada (m/s)

        Returns:
            int: Diametro en mm
        """
        cms = self.cfm_to_cms(cfm)
        area = cms / target_velocity  # m²
        diameter = math.sqrt(4 * area / math.pi) * 1000  # mm

        # Redondear al tamano estandar superior
        for std_size in self.CIRCULAR_SIZES:
            if std_size >= diameter:
                return std_size

        return self.CIRCULAR_SIZES[-1]

    def size_rectangular(self, cfm, target_velocity, preferred_height=None):
        """
        Calcula dimensiones de ducto rectangular.

        Args:
            cfm: Flujo en CFM
            target_velocity: Velocidad deseada (m/s)
            preferred_height: Altura preferida (mm)

        Returns:
            tuple: (width, height) en mm
        """
        cms = self.cfm_to_cms(cfm)
        area_required = cms / target_velocity * 1e6  # mm²

        best_size = None
        best_area_diff = float('inf')

        for width in self.RECTANGULAR_WIDTHS:
            for height in self.RECTANGULAR_HEIGHTS:
                # Verificar relacion de aspecto
                aspect = max(width, height) / min(width, height)
                if aspect > self.max_aspect:
                    continue

                area = width * height
                if area < area_required:
                    continue

                area_diff = area - area_required

                # Preferir altura especificada
                if preferred_height and height != preferred_height:
                    area_diff += 10000  # Penalizacion

                if area_diff < best_area_diff:
                    best_area_diff = area_diff
                    best_size = (width, height)

        if best_size is None:
            # Usar el mas grande
            return (self.RECTANGULAR_WIDTHS[-1], self.RECTANGULAR_HEIGHTS[-1])

        return best_size

    def calculate_equivalent_diameter(self, width, height):
        """Calcula diametro equivalente de ducto rectangular."""
        return 1.3 * ((width * height) ** 0.625) / ((width + height) ** 0.25)

    def calculate_velocity(self, cfm, width, height):
        """Calcula velocidad en ducto."""
        cms = self.cfm_to_cms(cfm)
        area = (width / 1000.0) * (height / 1000.0)
        return cms / area


class RectangularDuctBuilder:
    """Construye ductos rectangulares."""

    def __init__(self, wall_thickness=0.001):
        """
        Args:
            wall_thickness: Espesor de pared (m), default 1mm
        """
        self.wall_thickness = wall_thickness

    def build_straight_segment(self, start_point, end_point, width, height):
        """
        Construye segmento recto de ducto rectangular.

        Args:
            start_point: Punto inicial
            end_point: Punto final
            width: Ancho (mm)
            height: Altura (mm)

        Returns:
            DuctSegment
        """
        # Convertir a metros
        w = width / 1000.0
        h = height / 1000.0

        # Direccion y longitud
        direction = rg.Vector3d(end_point - start_point)
        length = direction.Length
        direction.Unitize()

        # Plano en el inicio
        up = rg.Vector3d.ZAxis
        if abs(rg.Vector3d.ZAxis * direction) > 0.99:
            up = rg.Vector3d.YAxis

        lateral = rg.Vector3d.CrossProduct(direction, up)
        lateral.Unitize()
        up = rg.Vector3d.CrossProduct(lateral, direction)

        plane = rg.Plane(start_point, lateral, up)

        # Crear rectangulo
        rect = rg.Rectangle3d(
            plane,
            rg.Interval(-w/2, w/2),
            rg.Interval(-h/2, h/2)
        )

        # Extruir
        profile = rect.ToNurbsCurve()
        extrusion = rg.Extrusion.Create(profile, length, True)

        # Linea central
        centerline = rg.LineCurve(start_point, end_point)

        return DuctSegment(
            brep=extrusion.ToBrep() if extrusion else None,
            centerline=centerline,
            start_size=(width, height),
            end_size=(width, height),
            length=length,
            type='rectangular_straight',
            cfm=0,  # Se asigna externamente
            velocity=0
        )

    def build_transition(self, start_point, end_point,
                          start_width, start_height,
                          end_width, end_height):
        """
        Construye transicion rectangular.

        Args:
            start_point, end_point: Puntos
            start_width, start_height: Dimensiones inicio (mm)
            end_width, end_height: Dimensiones fin (mm)

        Returns:
            DuctSegment
        """
        # Convertir a metros
        sw = start_width / 1000.0
        sh = start_height / 1000.0
        ew = end_width / 1000.0
        eh = end_height / 1000.0

        direction = rg.Vector3d(end_point - start_point)
        length = direction.Length
        direction.Unitize()

        # Planos
        up = rg.Vector3d.ZAxis
        if abs(rg.Vector3d.ZAxis * direction) > 0.99:
            up = rg.Vector3d.YAxis

        lateral = rg.Vector3d.CrossProduct(direction, up)
        lateral.Unitize()
        up = rg.Vector3d.CrossProduct(lateral, direction)

        start_plane = rg.Plane(start_point, lateral, up)
        end_plane = rg.Plane(end_point, lateral, up)

        # Rectangulos
        start_rect = rg.Rectangle3d(
            start_plane,
            rg.Interval(-sw/2, sw/2),
            rg.Interval(-sh/2, sh/2)
        )

        end_rect = rg.Rectangle3d(
            end_plane,
            rg.Interval(-ew/2, ew/2),
            rg.Interval(-eh/2, eh/2)
        )

        # Loft
        loft = rg.Brep.CreateFromLoft(
            [start_rect.ToNurbsCurve(), end_rect.ToNurbsCurve()],
            rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal, False
        )

        centerline = rg.LineCurve(start_point, end_point)

        return DuctSegment(
            brep=loft[0] if loft else None,
            centerline=centerline,
            start_size=(start_width, start_height),
            end_size=(end_width, end_height),
            length=length,
            type='rectangular_transition',
            cfm=0,
            velocity=0
        )

    def build_elbow(self, center, start_direction, end_direction,
                     width, height, radius_ratio=1.5):
        """
        Construye codo rectangular.

        Args:
            center: Centro del codo
            start_direction: Direccion de entrada
            end_direction: Direccion de salida
            width, height: Dimensiones (mm)
            radius_ratio: Radio/Ancho

        Returns:
            DuctFitting
        """
        w = width / 1000.0
        h = height / 1000.0
        radius = w * radius_ratio

        # Calcular angulo
        angle = rg.Vector3d.VectorAngle(start_direction, end_direction)

        # Crear arco del centerline
        start_dir = rg.Vector3d(start_direction)
        start_dir.Unitize()
        end_dir = rg.Vector3d(end_direction)
        end_dir.Unitize()

        # Punto de inicio del arco
        arc_start = rg.Point3d(
            center.X - start_dir.X * radius,
            center.Y - start_dir.Y * radius,
            center.Z - start_dir.Z * radius
        )

        # Punto final del arco
        arc_end = rg.Point3d(
            center.X + end_dir.X * radius,
            center.Y + end_dir.Y * radius,
            center.Z + end_dir.Z * radius
        )

        # Punto medio
        mid_dir = rg.Vector3d(start_dir + end_dir)
        mid_dir.Unitize()
        arc_mid = rg.Point3d(
            center.X + mid_dir.X * radius,
            center.Y + mid_dir.Y * radius,
            center.Z + mid_dir.Z * radius
        )

        # Crear arco
        arc = rg.Arc(arc_start, arc_mid, arc_end)
        arc_curve = arc.ToNurbsCurve()

        # Crear perfil rectangular
        up = rg.Vector3d.ZAxis
        lateral = rg.Vector3d.CrossProduct(start_dir, up)
        if lateral.Length < 0.01:
            lateral = rg.Vector3d.YAxis
        lateral.Unitize()
        up = rg.Vector3d.CrossProduct(lateral, start_dir)

        profile_plane = rg.Plane(arc_start, lateral, up)
        rect = rg.Rectangle3d(
            profile_plane,
            rg.Interval(-w/2, w/2),
            rg.Interval(-h/2, h/2)
        )

        # Sweep
        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(arc_curve, rect.ToNurbsCurve())

        # Coeficiente de perdida
        if radius_ratio >= 2.0:
            loss_coef = 0.10
        elif radius_ratio >= 1.5:
            loss_coef = 0.15
        else:
            loss_coef = 0.22

        return DuctFitting(
            brep=breps[0] if breps else None,
            type='rectangular_elbow',
            size=(width, height),
            angle=math.degrees(angle),
            loss_coefficient=loss_coef
        )


class CircularDuctBuilder:
    """Construye ductos circulares."""

    def __init__(self):
        pass

    def build_straight_segment(self, start_point, end_point, diameter):
        """
        Construye segmento recto de ducto circular.

        Args:
            start_point, end_point: Puntos
            diameter: Diametro (mm)

        Returns:
            DuctSegment
        """
        r = diameter / 2000.0  # Radio en metros

        direction = rg.Vector3d(end_point - start_point)
        length = direction.Length
        direction.Unitize()

        # Crear circulo
        plane = rg.Plane(start_point, direction)
        circle = rg.Circle(plane, r)

        # Extruir
        cylinder = rg.Cylinder(circle, length)
        brep = rg.Brep.CreateFromCylinder(cylinder, True, True)

        centerline = rg.LineCurve(start_point, end_point)

        return DuctSegment(
            brep=brep,
            centerline=centerline,
            start_size=diameter,
            end_size=diameter,
            length=length,
            type='circular_straight',
            cfm=0,
            velocity=0
        )

    def build_reducer(self, start_point, end_point,
                       start_diameter, end_diameter):
        """
        Construye reduccion circular.

        Args:
            start_point, end_point: Puntos
            start_diameter, end_diameter: Diametros (mm)

        Returns:
            DuctSegment
        """
        r1 = start_diameter / 2000.0
        r2 = end_diameter / 2000.0

        direction = rg.Vector3d(end_point - start_point)
        length = direction.Length
        direction.Unitize()

        # Circulos
        start_plane = rg.Plane(start_point, direction)
        end_plane = rg.Plane(end_point, direction)

        start_circle = rg.Circle(start_plane, r1)
        end_circle = rg.Circle(end_plane, r2)

        # Loft
        loft = rg.Brep.CreateFromLoft(
            [start_circle.ToNurbsCurve(), end_circle.ToNurbsCurve()],
            rg.Point3d.Unset, rg.Point3d.Unset,
            rg.LoftType.Normal, False
        )

        centerline = rg.LineCurve(start_point, end_point)

        return DuctSegment(
            brep=loft[0] if loft else None,
            centerline=centerline,
            start_size=start_diameter,
            end_size=end_diameter,
            length=length,
            type='circular_reducer',
            cfm=0,
            velocity=0
        )

    def build_elbow(self, center, start_direction, end_direction,
                     diameter, radius_ratio=1.5):
        """
        Construye codo circular.

        Args:
            center: Centro del codo
            start_direction, end_direction: Direcciones
            diameter: Diametro (mm)
            radius_ratio: Radio/Diametro

        Returns:
            DuctFitting
        """
        r = diameter / 2000.0
        bend_radius = (diameter / 1000.0) * radius_ratio

        # Calcular angulo
        start_dir = rg.Vector3d(start_direction)
        start_dir.Unitize()
        end_dir = rg.Vector3d(end_direction)
        end_dir.Unitize()

        angle = rg.Vector3d.VectorAngle(start_dir, end_dir)

        # Crear arco
        arc_start = rg.Point3d(
            center.X - start_dir.X * bend_radius,
            center.Y - start_dir.Y * bend_radius,
            center.Z - start_dir.Z * bend_radius
        )

        arc_end = rg.Point3d(
            center.X + end_dir.X * bend_radius,
            center.Y + end_dir.Y * bend_radius,
            center.Z + end_dir.Z * bend_radius
        )

        mid_dir = rg.Vector3d(start_dir + end_dir)
        mid_dir.Unitize()
        arc_mid = rg.Point3d(
            center.X + mid_dir.X * bend_radius,
            center.Y + mid_dir.Y * bend_radius,
            center.Z + mid_dir.Z * bend_radius
        )

        arc = rg.Arc(arc_start, arc_mid, arc_end)
        arc_curve = arc.ToNurbsCurve()

        # Crear perfil circular
        profile_plane = rg.Plane(arc_start, start_dir)
        circle = rg.Circle(profile_plane, r)

        # Sweep
        sweep = rg.SweepOneRail()
        breps = sweep.PerformSweep(arc_curve, circle.ToNurbsCurve())

        # Coeficiente de perdida
        if radius_ratio >= 2.0:
            loss_coef = 0.08
        elif radius_ratio >= 1.5:
            loss_coef = 0.12
        else:
            loss_coef = 0.18

        return DuctFitting(
            brep=breps[0] if breps else None,
            type='circular_elbow',
            size=diameter,
            angle=math.degrees(angle),
            loss_coefficient=loss_coef
        )

    def build_tee(self, main_start, main_end, branch_point,
                   main_diameter, branch_diameter):
        """
        Construye tee circular.

        Args:
            main_start, main_end: Puntos del ducto principal
            branch_point: Punto de conexion del ramal
            main_diameter, branch_diameter: Diametros (mm)

        Returns:
            DuctFitting
        """
        main_segment = self.build_straight_segment(
            main_start, main_end, main_diameter
        )

        # Encontrar punto de interseccion
        main_dir = rg.Vector3d(main_end - main_start)
        main_line = rg.Line(main_start, main_end)

        # Proyectar branch_point a la linea principal
        t = main_line.ClosestParameter(branch_point)
        intersection = main_line.PointAt(t)

        # Crear ramal
        branch_segment = self.build_straight_segment(
            intersection, branch_point, branch_diameter
        )

        # Unir geometrias
        if main_segment.brep and branch_segment.brep:
            result = rg.Brep.CreateBooleanUnion(
                [main_segment.brep, branch_segment.brep], 0.001
            )
            if result:
                brep = result[0]
            else:
                brep = main_segment.brep
        else:
            brep = main_segment.brep

        return DuctFitting(
            brep=brep,
            type='circular_tee',
            size=(main_diameter, branch_diameter),
            angle=90,
            loss_coefficient=0.35
        )


class InsulationBuilder:
    """Construye aislamiento para ductos."""

    def __init__(self, thickness=25):
        """
        Args:
            thickness: Espesor de aislamiento (mm)
        """
        self.thickness = thickness / 1000.0  # Convertir a metros

    def build_rectangular_insulation(self, duct_brep, width, height, length):
        """
        Crea aislamiento para ducto rectangular.

        Args:
            duct_brep: Brep del ducto
            width, height, length: Dimensiones (mm)

        Returns:
            Brep: Aislamiento
        """
        # Obtener centro
        bbox = duct_brep.GetBoundingBox(True)
        center = bbox.Center

        # Dimensiones exteriores
        w_out = width / 1000.0 + 2 * self.thickness
        h_out = height / 1000.0 + 2 * self.thickness

        # Crear caja exterior
        plane = rg.Plane(center, rg.Vector3d.ZAxis)

        outer_box = rg.Box(
            plane,
            rg.Interval(-w_out/2, w_out/2),
            rg.Interval(-h_out/2, h_out/2),
            rg.Interval(-length/2000.0, length/2000.0)
        )

        outer_brep = outer_box.ToBrep()

        # Hacer diferencia booleana
        result = rg.Brep.CreateBooleanDifference(outer_brep, duct_brep, 0.001)

        if result and len(result) > 0:
            return result[0]

        return None

    def build_circular_insulation(self, duct_brep, diameter, length):
        """
        Crea aislamiento para ducto circular.

        Args:
            duct_brep: Brep del ducto
            diameter, length: Dimensiones (mm)

        Returns:
            Brep: Aislamiento
        """
        bbox = duct_brep.GetBoundingBox(True)
        center = bbox.Center

        # Radio exterior
        r_out = diameter / 2000.0 + self.thickness

        # Cilindro exterior
        plane = rg.Plane(
            rg.Point3d(center.X, center.Y, center.Z - length/2000.0),
            rg.Vector3d.ZAxis
        )

        outer_circle = rg.Circle(plane, r_out)
        outer_cylinder = rg.Cylinder(outer_circle, length / 1000.0)
        outer_brep = rg.Brep.CreateFromCylinder(outer_cylinder, True, True)

        # Diferencia
        result = rg.Brep.CreateBooleanDifference(outer_brep, duct_brep, 0.001)

        if result and len(result) > 0:
            return result[0]

        return None


class DuctRunBuilder:
    """Construye corrida completa de ductos."""

    def __init__(self, duct_type='rectangular'):
        """
        Args:
            duct_type: 'rectangular' o 'circular'
        """
        self.duct_type = duct_type
        self.sizer = DuctSizer()

        if duct_type == 'rectangular':
            self.builder = RectangularDuctBuilder()
        else:
            self.builder = CircularDuctBuilder()

    def build_run_from_points(self, points, cfm, velocity=8.0):
        """
        Construye corrida de ductos desde lista de puntos.

        Args:
            points: Lista de Point3d
            cfm: Flujo de aire
            velocity: Velocidad objetivo

        Returns:
            DuctRun
        """
        segments = []
        fittings = []
        total_length = 0
        total_area = 0

        if len(points) < 2:
            return None

        # Dimensionar ducto
        if self.duct_type == 'rectangular':
            width, height = self.sizer.size_rectangular(cfm, velocity)
            size = (width, height)
        else:
            diameter = self.sizer.size_circular(cfm, velocity)
            size = diameter

        # Construir segmentos
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]

            if self.duct_type == 'rectangular':
                segment = self.builder.build_straight_segment(
                    start, end, width, height
                )
                area = (width / 1000.0) * (height / 1000.0) * 2 * segment.length
            else:
                segment = self.builder.build_straight_segment(
                    start, end, diameter
                )
                area = math.pi * (diameter / 1000.0) * segment.length

            segments.append(segment)
            total_length += segment.length
            total_area += area

            # Agregar codo si hay cambio de direccion
            if i < len(points) - 2:
                dir1 = rg.Vector3d(points[i + 1] - points[i])
                dir2 = rg.Vector3d(points[i + 2] - points[i + 1])

                angle = rg.Vector3d.VectorAngle(dir1, dir2)
                if angle > 0.1:  # Mas de ~6 grados
                    if self.duct_type == 'rectangular':
                        fitting = self.builder.build_elbow(
                            points[i + 1], dir1, dir2, width, height
                        )
                    else:
                        fitting = self.builder.build_elbow(
                            points[i + 1], dir1, dir2, diameter
                        )
                    fittings.append(fitting)

        # Calcular caida de presion aproximada
        pressure_drop = self._calculate_pressure_drop(
            segments, fittings, velocity
        )

        return DuctRun(
            segments=segments,
            fittings=fittings,
            total_length=total_length,
            total_area=total_area,
            pressure_drop=pressure_drop,
            cfm=cfm
        )

    def _calculate_pressure_drop(self, segments, fittings, velocity):
        """Calcula caida de presion aproximada."""
        # Perdida por friccion (aproximada)
        friction_loss = 0.1  # Pa/m tipico
        total_length = sum(s.length for s in segments)
        friction_drop = friction_loss * total_length

        # Perdida por accesorios
        dynamic_pressure = 0.6 * velocity ** 2  # Pa
        fitting_drop = sum(
            f.loss_coefficient * dynamic_pressure
            for f in fittings
        )

        return friction_drop + fitting_drop


# Funciones de utilidad
def create_duct_path(points, cfm, duct_type='rectangular', velocity=8.0):
    """
    Funcion rapida para crear ducto desde puntos.

    Returns:
        DuctRun
    """
    builder = DuctRunBuilder(duct_type)
    return builder.build_run_from_points(points, cfm, velocity)


# Ejemplo de uso
if __name__ == "__main__":
    # Puntos de prueba
    points = [
        rg.Point3d(0, 0, 3),
        rg.Point3d(5, 0, 3),
        rg.Point3d(5, 8, 3),
        rg.Point3d(12, 8, 3)
    ]

    # Crear corrida de ducto
    run = create_duct_path(points, cfm=2000, duct_type='rectangular')

    print(f"Segmentos: {len(run.segments)}")
    print(f"Accesorios: {len(run.fittings)}")
    print(f"Longitud total: {run.total_length:.2f} m")
    print(f"Area total: {run.total_area:.2f} m2")
    print(f"Caida de presion: {run.pressure_drop:.1f} Pa")
