#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constructor de Equipos - M02 Sistema HVAC Modular

Genera geometria de equipos HVAC: UMAs, cajas VAV,
fan coils, y equipos de zona.

Autor: BIMAC
Version: 1.0.0
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple

# Estructuras de datos
EquipmentGeometry = namedtuple('EquipmentGeometry', [
    'brep', 'location', 'dimensions', 'type',
    'capacity_cfm', 'connections', 'weight'
])

Connection = namedtuple('Connection', [
    'point', 'direction', 'size', 'type'
])


class AHUDatabase:
    """Base de datos de Unidades Manejadoras de Aire."""

    MODELS = {
        'AHU-1000': {
            'cfm': 1000,
            'dimensions': (1200, 800, 1000),
            'weight': 250,
            'connections': {
                'supply': {'size': 300, 'position': 'top'},
                'return': {'size': 300, 'position': 'side'},
                'outdoor': {'size': 200, 'position': 'back'},
                'exhaust': {'size': 200, 'position': 'back'}
            }
        },
        'AHU-2500': {
            'cfm': 2500,
            'dimensions': (1500, 1000, 1200),
            'weight': 450,
            'connections': {
                'supply': {'size': 450, 'position': 'top'},
                'return': {'size': 450, 'position': 'side'},
                'outdoor': {'size': 300, 'position': 'back'},
                'exhaust': {'size': 300, 'position': 'back'}
            }
        },
        'AHU-5000': {
            'cfm': 5000,
            'dimensions': (2000, 1200, 1500),
            'weight': 750,
            'connections': {
                'supply': {'size': 600, 'position': 'top'},
                'return': {'size': 600, 'position': 'side'},
                'outdoor': {'size': 400, 'position': 'back'},
                'exhaust': {'size': 400, 'position': 'back'}
            }
        },
        'AHU-10000': {
            'cfm': 10000,
            'dimensions': (2500, 1500, 1800),
            'weight': 1200,
            'connections': {
                'supply': {'size': 800, 'position': 'top'},
                'return': {'size': 800, 'position': 'side'},
                'outdoor': {'size': 500, 'position': 'back'},
                'exhaust': {'size': 500, 'position': 'back'}
            }
        },
        'AHU-20000': {
            'cfm': 20000,
            'dimensions': (3000, 2000, 2200),
            'weight': 2000,
            'connections': {
                'supply': {'size': 1000, 'position': 'top'},
                'return': {'size': 1000, 'position': 'side'},
                'outdoor': {'size': 700, 'position': 'back'},
                'exhaust': {'size': 700, 'position': 'back'}
            }
        }
    }

    @classmethod
    def get_model(cls, model_name):
        return cls.MODELS.get(model_name, cls.MODELS['AHU-5000'])

    @classmethod
    def select_by_cfm(cls, cfm):
        """Selecciona modelo por capacidad."""
        for name, data in sorted(cls.MODELS.items(), key=lambda x: x[1]['cfm']):
            if data['cfm'] >= cfm:
                return name, data
        return 'AHU-20000', cls.MODELS['AHU-20000']


class AHUBuilder:
    """Construye Unidades Manejadoras de Aire."""

    def __init__(self):
        pass

    def build(self, location, model_name=None, cfm=None, rotation=0):
        """
        Construye UMA.

        Args:
            location: Punto de ubicacion (esquina inferior)
            model_name: Nombre del modelo (o None para auto-seleccionar)
            cfm: Capacidad requerida
            rotation: Rotacion en grados

        Returns:
            EquipmentGeometry
        """
        if model_name:
            data = AHUDatabase.get_model(model_name)
        elif cfm:
            model_name, data = AHUDatabase.select_by_cfm(cfm)
        else:
            model_name = 'AHU-5000'
            data = AHUDatabase.get_model(model_name)

        # Dimensiones
        length = data['dimensions'][0] / 1000.0
        width = data['dimensions'][1] / 1000.0
        height = data['dimensions'][2] / 1000.0

        # Crear caja base
        plane = rg.Plane(location, rg.Vector3d.ZAxis)

        if rotation != 0:
            plane.Rotate(math.radians(rotation), rg.Vector3d.ZAxis)

        box = rg.Box(
            plane,
            rg.Interval(0, length),
            rg.Interval(0, width),
            rg.Interval(0, height)
        )

        brep = box.ToBrep()

        # Generar conexiones
        connections = self._create_connections(location, data, rotation)

        return EquipmentGeometry(
            brep=brep,
            location=location,
            dimensions=data['dimensions'],
            type='AHU',
            capacity_cfm=data['cfm'],
            connections=connections,
            weight=data['weight']
        )

    def _create_connections(self, location, data, rotation):
        """Crea puntos de conexion."""
        connections = []
        dims = data['dimensions']

        length = dims[0] / 1000.0
        width = dims[1] / 1000.0
        height = dims[2] / 1000.0

        for conn_name, conn_data in data['connections'].items():
            size = conn_data['size']
            position = conn_data['position']

            # Calcular posicion del punto de conexion
            if position == 'top':
                point = rg.Point3d(
                    location.X + length / 2,
                    location.Y + width / 2,
                    location.Z + height
                )
                direction = rg.Vector3d.ZAxis
            elif position == 'side':
                point = rg.Point3d(
                    location.X + length,
                    location.Y + width / 2,
                    location.Z + height / 2
                )
                direction = rg.Vector3d.XAxis
            elif position == 'back':
                point = rg.Point3d(
                    location.X + length / 2,
                    location.Y,
                    location.Z + height / 2
                )
                direction = -rg.Vector3d.YAxis
            else:
                point = location
                direction = rg.Vector3d.ZAxis

            # Aplicar rotacion
            if rotation != 0:
                transform = rg.Transform.Rotation(
                    math.radians(rotation), rg.Vector3d.ZAxis, location
                )
                point.Transform(transform)
                direction.Transform(transform)

            connections.append(Connection(
                point=point,
                direction=direction,
                size=size,
                type=conn_name
            ))

        return connections


class VAVBoxBuilder:
    """Construye cajas VAV."""

    VAV_SIZES = {
        150: {'cfm_range': (50, 250), 'dimensions': (350, 250, 250)},
        200: {'cfm_range': (100, 450), 'dimensions': (400, 300, 300)},
        250: {'cfm_range': (200, 700), 'dimensions': (450, 350, 350)},
        300: {'cfm_range': (300, 1000), 'dimensions': (500, 400, 400)},
        350: {'cfm_range': (400, 1400), 'dimensions': (550, 450, 450)},
        400: {'cfm_range': (600, 2000), 'dimensions': (600, 500, 500)},
    }

    def __init__(self):
        pass

    def select_size(self, cfm):
        """Selecciona tamano de caja por CFM."""
        for size, data in sorted(self.VAV_SIZES.items()):
            if data['cfm_range'][0] <= cfm <= data['cfm_range'][1]:
                return size, data
        return 400, self.VAV_SIZES[400]

    def build(self, location, cfm, inlet_direction=None):
        """
        Construye caja VAV.

        Args:
            location: Punto de ubicacion
            cfm: Flujo de aire
            inlet_direction: Direccion de entrada

        Returns:
            EquipmentGeometry
        """
        size, data = self.select_size(cfm)

        dims = data['dimensions']
        length = dims[0] / 1000.0
        width = dims[1] / 1000.0
        height = dims[2] / 1000.0

        # Crear caja
        center = rg.Point3d(
            location.X - length / 2,
            location.Y - width / 2,
            location.Z - height / 2
        )

        box = rg.Box(
            rg.Plane(center, rg.Vector3d.ZAxis),
            rg.Interval(0, length),
            rg.Interval(0, width),
            rg.Interval(0, height)
        )

        # Conexiones
        inlet = Connection(
            point=rg.Point3d(location.X - length/2, location.Y, location.Z),
            direction=-rg.Vector3d.XAxis,
            size=size,
            type='inlet'
        )

        outlet = Connection(
            point=rg.Point3d(location.X + length/2, location.Y, location.Z),
            direction=rg.Vector3d.XAxis,
            size=size - 50,  # Outlet ligeramente menor
            type='outlet'
        )

        return EquipmentGeometry(
            brep=box.ToBrep(),
            location=location,
            dimensions=dims,
            type='VAV_box',
            capacity_cfm=cfm,
            connections=[inlet, outlet],
            weight=15  # kg aproximado
        )


class FanCoilBuilder:
    """Construye unidades Fan Coil."""

    TYPES = {
        'horizontal_concealed': {
            'heights': [200, 250, 300],
            'width': 600,
            'cfm_per_height': {200: 400, 250: 600, 300: 800}
        },
        'vertical_exposed': {
            'heights': [600, 750, 900],
            'width': 300,
            'depth': 600,
            'cfm_per_height': {600: 500, 750: 700, 900: 900}
        },
        'cassette': {
            'sizes': [(600, 600), (840, 840)],
            'height': 250,
            'cfm_per_size': {600: 600, 840: 1200}
        }
    }

    def __init__(self):
        pass

    def build_horizontal(self, location, cfm, length=1200):
        """
        Construye fan coil horizontal oculto.

        Args:
            location: Punto de ubicacion
            cfm: Capacidad
            length: Longitud de la unidad

        Returns:
            EquipmentGeometry
        """
        type_data = self.TYPES['horizontal_concealed']

        # Seleccionar altura por CFM
        height = type_data['heights'][0]
        for h in type_data['heights']:
            if type_data['cfm_per_height'][h] >= cfm:
                height = h
                break

        width = type_data['width']

        # Dimensiones en metros
        l = length / 1000.0
        w = width / 1000.0
        h = height / 1000.0

        # Crear caja
        box = rg.Box(
            rg.Plane(location, rg.Vector3d.ZAxis),
            rg.Interval(0, l),
            rg.Interval(-w/2, w/2),
            rg.Interval(0, h)
        )

        # Conexiones
        supply = Connection(
            point=rg.Point3d(location.X + l/2, location.Y, location.Z),
            direction=-rg.Vector3d.ZAxis,
            size=200,
            type='supply_air'
        )

        return_conn = Connection(
            point=rg.Point3d(location.X + l/2, location.Y, location.Z + h),
            direction=rg.Vector3d.ZAxis,
            size=200,
            type='return_air'
        )

        return EquipmentGeometry(
            brep=box.ToBrep(),
            location=location,
            dimensions=(length, width, height),
            type='fan_coil_horizontal',
            capacity_cfm=cfm,
            connections=[supply, return_conn],
            weight=35
        )

    def build_cassette(self, location, cfm):
        """
        Construye fan coil cassette de techo.

        Args:
            location: Centro del cassette
            cfm: Capacidad

        Returns:
            EquipmentGeometry
        """
        type_data = self.TYPES['cassette']

        # Seleccionar tamano
        if cfm <= 600:
            size = 600
        else:
            size = 840

        height = type_data['height']

        # Dimensiones en metros
        s = size / 1000.0
        h = height / 1000.0

        # Crear caja centrada
        box = rg.Box(
            rg.Plane(
                rg.Point3d(location.X - s/2, location.Y - s/2, location.Z),
                rg.Vector3d.ZAxis
            ),
            rg.Interval(0, s),
            rg.Interval(0, s),
            rg.Interval(0, h)
        )

        # Conexion de suministro (ducto)
        supply = Connection(
            point=rg.Point3d(location.X, location.Y, location.Z + h),
            direction=rg.Vector3d.ZAxis,
            size=200,
            type='supply_duct'
        )

        return EquipmentGeometry(
            brep=box.ToBrep(),
            location=location,
            dimensions=(size, size, height),
            type='fan_coil_cassette',
            capacity_cfm=cfm,
            connections=[supply],
            weight=45
        )


class ExhaustFanBuilder:
    """Construye ventiladores de extraccion."""

    SIZES = {
        100: {'cfm': 100, 'dimensions': (300, 300, 200), 'power': 50},
        200: {'cfm': 300, 'dimensions': (400, 400, 250), 'power': 100},
        300: {'cfm': 600, 'dimensions': (500, 500, 300), 'power': 180},
        400: {'cfm': 1000, 'dimensions': (600, 600, 350), 'power': 280},
        500: {'cfm': 1500, 'dimensions': (700, 700, 400), 'power': 400},
    }

    def __init__(self):
        pass

    def build_inline(self, location, cfm, direction=None):
        """
        Construye extractor en linea.

        Args:
            location: Ubicacion
            cfm: Capacidad
            direction: Direccion del flujo

        Returns:
            EquipmentGeometry
        """
        # Seleccionar tamano
        size = 100
        for s, data in sorted(self.SIZES.items()):
            if data['cfm'] >= cfm:
                size = s
                break

        data = self.SIZES[size]
        dims = data['dimensions']

        # Crear cilindro
        if direction is None:
            direction = rg.Vector3d.ZAxis

        plane = rg.Plane(location, direction)
        circle = rg.Circle(plane, dims[0] / 2000.0)
        cylinder = rg.Cylinder(circle, dims[2] / 1000.0)
        brep = rg.Brep.CreateFromCylinder(cylinder, True, True)

        # Conexiones
        inlet = Connection(
            point=location,
            direction=-direction,
            size=size,
            type='inlet'
        )

        outlet = Connection(
            point=rg.Point3d(
                location.X + direction.X * dims[2] / 1000.0,
                location.Y + direction.Y * dims[2] / 1000.0,
                location.Z + direction.Z * dims[2] / 1000.0
            ),
            direction=direction,
            size=size,
            type='outlet'
        )

        return EquipmentGeometry(
            brep=brep,
            location=location,
            dimensions=dims,
            type='exhaust_fan_inline',
            capacity_cfm=data['cfm'],
            connections=[inlet, outlet],
            weight=data['power'] / 10  # Aproximacion
        )


class HVACEquipmentAssembly:
    """Ensambla sistema completo de equipos."""

    def __init__(self):
        self.ahu_builder = AHUBuilder()
        self.vav_builder = VAVBoxBuilder()
        self.fc_builder = FanCoilBuilder()
        self.fan_builder = ExhaustFanBuilder()

    def build_vav_system(self, ahu_location, zone_points, total_cfm):
        """
        Construye sistema VAV completo.

        Args:
            ahu_location: Ubicacion de la UMA
            zone_points: Lista de puntos de zona
            total_cfm: CFM total del sistema

        Returns:
            dict: Equipos del sistema
        """
        equipment = {}

        # UMA
        equipment['ahu'] = self.ahu_builder.build(
            ahu_location, cfm=total_cfm
        )

        # Cajas VAV por zona
        cfm_per_zone = total_cfm / len(zone_points)
        equipment['vav_boxes'] = []

        for i, point in enumerate(zone_points):
            vav = self.vav_builder.build(point, cfm_per_zone)
            equipment['vav_boxes'].append(vav)

        return equipment

    def build_fan_coil_system(self, unit_locations, cfm_per_unit):
        """
        Construye sistema de fan coils.

        Args:
            unit_locations: Lista de ubicaciones
            cfm_per_unit: CFM por unidad

        Returns:
            list: Lista de fan coils
        """
        units = []

        for location in unit_locations:
            fc = self.fc_builder.build_cassette(location, cfm_per_unit)
            units.append(fc)

        return units


# Ejemplo de uso
if __name__ == "__main__":
    # Construir UMA
    ahu_builder = AHUBuilder()
    ahu = ahu_builder.build(
        rg.Point3d(0, 0, 0),
        cfm=5000
    )

    print(f"UMA: {ahu.type}")
    print(f"Dimensiones: {ahu.dimensions}")
    print(f"Capacidad: {ahu.capacity_cfm} CFM")
    print(f"Conexiones: {len(ahu.connections)}")

    # Construir caja VAV
    vav_builder = VAVBoxBuilder()
    vav = vav_builder.build(
        rg.Point3d(10, 5, 3),
        cfm=800
    )

    print(f"\nVAV: {vav.type}")
    print(f"Capacidad: {vav.capacity_cfm} CFM")
