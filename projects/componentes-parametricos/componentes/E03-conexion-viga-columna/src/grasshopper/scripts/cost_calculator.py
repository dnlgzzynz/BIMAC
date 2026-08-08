#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculador de Costos - E03 Conexion Viga-Columna Parametrica

Calcula costos detallados de materiales, fabricacion e instalacion
para conexiones estructurales acero segun tipo y complejidad.

Autor: BIMAC
Version: 1.0.0
"""

from collections import namedtuple
import math

# Estructuras de datos
MaterialCost = namedtuple('MaterialCost', ['item', 'quantity', 'unit', 'unit_price', 'total'])
LaborCost = namedtuple('LaborCost', ['operation', 'hours', 'rate', 'total'])
CostBreakdown = namedtuple('CostBreakdown', [
    'materials', 'labor', 'equipment', 'overhead',
    'subtotal', 'contingency', 'total'
])


class SteelMaterialDatabase:
    """Base de datos de costos de materiales de acero."""

    # Precios en USD/kg segun grado de acero
    STEEL_PRICES = {
        'A36': 1.25,
        'A572_Gr50': 1.35,
        'A992': 1.40,
        'A500_Gr_B': 1.30,
        'A500_Gr_C': 1.35
    }

    # Densidad del acero kg/m3
    STEEL_DENSITY = 7850.0

    # Precios de tornillos USD/unidad
    BOLT_PRICES = {
        'A325': {
            16: {'bolt': 1.20, 'nut': 0.45, 'washer': 0.25},
            19: {'bolt': 1.65, 'nut': 0.55, 'washer': 0.30},
            22: {'bolt': 2.10, 'nut': 0.70, 'washer': 0.35},
            25: {'bolt': 2.85, 'nut': 0.90, 'washer': 0.45},
            28: {'bolt': 3.60, 'nut': 1.15, 'washer': 0.55},
            32: {'bolt': 4.80, 'nut': 1.50, 0.70}
        },
        'A490': {
            16: {'bolt': 1.80, 'nut': 0.55, 'washer': 0.30},
            19: {'bolt': 2.45, 'nut': 0.70, 'washer': 0.35},
            22: {'bolt': 3.15, 'nut': 0.85, 'washer': 0.45},
            25: {'bolt': 4.25, 'nut': 1.10, 'washer': 0.55},
            28: {'bolt': 5.40, 'nut': 1.40, 'washer': 0.70},
            32: {'bolt': 7.20, 'nut': 1.85, 'washer': 0.85}
        }
    }

    # Precios de soldadura USD/kg de electrodo
    WELD_ELECTRODE_PRICES = {
        'E70': 4.50,
        'E80': 5.80
    }

    # Factor de consumo de electrodo (kg electrodo / kg metal depositado)
    ELECTRODE_CONSUMPTION = {
        'SMAW': 1.65,
        'FCAW': 1.20,
        'GMAW': 1.05,
        'SAW': 1.02
    }

    def get_steel_price(self, grade):
        """Obtiene precio del acero por kg."""
        return self.STEEL_PRICES.get(grade, 1.35)

    def get_bolt_set_price(self, grade, diameter):
        """Obtiene precio de set tornillo + tuerca + 2 arandelas."""
        if grade in self.BOLT_PRICES and diameter in self.BOLT_PRICES[grade]:
            prices = self.BOLT_PRICES[grade][diameter]
            return prices['bolt'] + prices['nut'] + 2 * prices['washer']
        return 3.50  # Precio default

    def get_weld_price_per_kg(self, electrode, process='FCAW'):
        """Obtiene precio por kg de metal depositado."""
        base_price = self.WELD_ELECTRODE_PRICES.get(electrode, 5.00)
        consumption = self.ELECTRODE_CONSUMPTION.get(process, 1.20)
        return base_price * consumption


class LaborRateDatabase:
    """Base de datos de tasas de mano de obra."""

    # Tasas por hora USD
    LABOR_RATES = {
        'welder_certified': 45.00,
        'welder_standard': 35.00,
        'ironworker': 42.00,
        'fitter': 38.00,
        'helper': 22.00,
        'crane_operator': 55.00,
        'inspector': 65.00,
        'supervisor': 75.00
    }

    # Horas por operacion (base)
    OPERATION_HOURS = {
        # Corte
        'cut_plate_simple': 0.15,      # Por corte recto
        'cut_plate_complex': 0.35,     # Por corte con forma
        'cut_rbs': 0.50,               # Corte RBS

        # Perforacion
        'drill_hole': 0.05,            # Por agujero
        'punch_hole': 0.02,            # Por agujero (punzonado)

        # Soldadura
        'weld_fillet_per_inch': 0.08,  # Por pulgada de filete
        'weld_cjp_per_inch': 0.25,     # Por pulgada de CJP
        'weld_pjp_per_inch': 0.15,     # Por pulgada de PJP
        'weld_backing_bar': 0.20,      # Instalar backing bar

        # Instalacion de tornillos
        'bolt_snug': 0.03,             # Por tornillo apretado
        'bolt_pretension': 0.08,       # Por tornillo pretensado
        'bolt_slip_critical': 0.10,    # Por tornillo slip-critical

        # Ensamble
        'fit_plate': 0.25,             # Ajustar placa
        'fit_stiffener': 0.35,         # Ajustar rigidizador
        'tack_weld': 0.10,             # Puntear

        # Campo
        'erection_simple': 1.00,       # Conexion simple
        'erection_moment': 2.50,       # Conexion de momento
        'erection_seismic': 3.50,      # Conexion sismica
        'alignment': 0.50,             # Alineacion
        'inspection': 0.75             # Inspeccion
    }

    def get_rate(self, worker_type):
        """Obtiene tasa horaria."""
        return self.LABOR_RATES.get(worker_type, 35.00)

    def get_operation_hours(self, operation):
        """Obtiene horas base por operacion."""
        return self.OPERATION_HOURS.get(operation, 0.25)


class PlateCalculator:
    """Calcula peso y costo de placas."""

    def __init__(self, material_db):
        self.material_db = material_db
        self.density = 7850.0  # kg/m3

    def calculate_plate_weight(self, length, width, thickness):
        """
        Calcula peso de placa rectangular.

        Args:
            length: Longitud en mm
            width: Ancho en mm
            thickness: Espesor en mm

        Returns:
            float: Peso en kg
        """
        volume_m3 = (length / 1000.0) * (width / 1000.0) * (thickness / 1000.0)
        return volume_m3 * self.density

    def calculate_plate_cost(self, length, width, thickness, material='A36'):
        """Calcula costo de placa."""
        weight = self.calculate_plate_weight(length, width, thickness)
        price_per_kg = self.material_db.get_steel_price(material)
        return weight, weight * price_per_kg


class BoltCalculator:
    """Calcula costos de tornilleria."""

    def __init__(self, material_db):
        self.material_db = material_db

    def calculate_bolt_cost(self, count, diameter, grade, include_washer=True):
        """
        Calcula costo de tornillos.

        Args:
            count: Numero de tornillos
            diameter: Diametro en mm
            grade: Grado (A325, A490)
            include_washer: Incluir arandelas

        Returns:
            float: Costo total
        """
        unit_price = self.material_db.get_bolt_set_price(grade, diameter)
        return count * unit_price


class WeldCalculator:
    """Calcula costos de soldadura."""

    def __init__(self, material_db):
        self.material_db = material_db

    # Peso de metal depositado kg/mm de soldadura por mm de longitud
    # Para filete: area = 0.5 * leg^2
    # Para CJP: area = thickness * groove_width

    def calculate_fillet_weight(self, length_mm, leg_mm):
        """Calcula peso de soldadura de filete."""
        area_mm2 = 0.5 * leg_mm * leg_mm
        volume_mm3 = area_mm2 * length_mm
        volume_m3 = volume_mm3 / 1e9
        return volume_m3 * 7850.0

    def calculate_cjp_weight(self, length_mm, thickness_mm, groove_angle=60):
        """Calcula peso de soldadura CJP."""
        # Aproximacion: groove area + reinforcement
        groove_width = thickness_mm * math.tan(math.radians(groove_angle / 2)) * 2
        area_mm2 = thickness_mm * groove_width * 0.6  # Factor de llenado
        volume_mm3 = area_mm2 * length_mm
        volume_m3 = volume_mm3 / 1e9
        return volume_m3 * 7850.0

    def calculate_weld_cost(self, weld_type, length_mm, size_mm, electrode='E70'):
        """
        Calcula costo de soldadura.

        Args:
            weld_type: 'fillet' o 'cjp'
            length_mm: Longitud en mm
            size_mm: Pierna (filete) o espesor (CJP) en mm
            electrode: Tipo de electrodo

        Returns:
            tuple: (peso_kg, costo_material)
        """
        if weld_type == 'fillet':
            weight = self.calculate_fillet_weight(length_mm, size_mm)
        else:
            weight = self.calculate_cjp_weight(length_mm, size_mm)

        price_per_kg = self.material_db.get_weld_price_per_kg(electrode)
        return weight, weight * price_per_kg


class ConnectionCostCalculator:
    """Calculador principal de costos de conexiones."""

    # Factores de complejidad por tipo de conexion
    COMPLEXITY_FACTORS = {
        'shear_tab': 1.0,
        'clip_angle': 1.1,
        'end_plate': 1.3,
        'extended_end_plate': 1.5,
        'directly_welded': 1.2,
        'RBS': 1.8,
        'WUF-W': 1.6,
        'WUF-B': 1.4,
        'BUEEP': 1.7,
        'BFP': 1.5
    }

    # Categorias sismicas y factores
    SEISMIC_FACTORS = {
        'none': 1.0,
        'OMF': 1.15,
        'IMF': 1.35,
        'SMF': 1.55
    }

    def __init__(self):
        self.material_db = SteelMaterialDatabase()
        self.labor_db = LaborRateDatabase()
        self.plate_calc = PlateCalculator(self.material_db)
        self.bolt_calc = BoltCalculator(self.material_db)
        self.weld_calc = WeldCalculator(self.material_db)

    def calculate_shear_tab_cost(self, config):
        """
        Calcula costo de conexion shear tab.

        Args:
            config: dict con:
                - plate_length, plate_width, plate_thickness
                - bolt_count, bolt_diameter, bolt_grade
                - weld_length, weld_size
                - material
        """
        materials = []
        labor = []

        # Placa
        plate_weight, plate_cost = self.plate_calc.calculate_plate_cost(
            config.get('plate_length', 300),
            config.get('plate_width', 100),
            config.get('plate_thickness', 10),
            config.get('material', 'A36')
        )
        materials.append(MaterialCost(
            'Shear tab plate', plate_weight, 'kg',
            self.material_db.get_steel_price(config.get('material', 'A36')),
            plate_cost
        ))

        # Tornillos
        bolt_count = config.get('bolt_count', 3)
        bolt_diam = config.get('bolt_diameter', 22)
        bolt_grade = config.get('bolt_grade', 'A325')
        bolt_cost = self.bolt_calc.calculate_bolt_cost(
            bolt_count, bolt_diam, bolt_grade
        )
        materials.append(MaterialCost(
            f'Bolts {bolt_grade} {bolt_diam}mm', bolt_count, 'pcs',
            self.material_db.get_bolt_set_price(bolt_grade, bolt_diam),
            bolt_cost
        ))

        # Soldadura
        weld_length = config.get('weld_length', 300)
        weld_size = config.get('weld_size', 8)
        weld_weight, weld_cost = self.weld_calc.calculate_weld_cost(
            'fillet', weld_length * 2, weld_size  # Ambos lados
        )
        materials.append(MaterialCost(
            'Fillet weld E70', weld_weight, 'kg',
            self.material_db.get_weld_price_per_kg('E70'),
            weld_cost
        ))

        # Mano de obra - Taller
        shop_hours = (
            self.labor_db.get_operation_hours('cut_plate_simple') * 4 +
            self.labor_db.get_operation_hours('drill_hole') * bolt_count +
            self.labor_db.get_operation_hours('fit_plate') +
            self.labor_db.get_operation_hours('weld_fillet_per_inch') * (weld_length * 2 / 25.4)
        )
        labor.append(LaborCost(
            'Shop fabrication', shop_hours,
            self.labor_db.get_rate('fitter'),
            shop_hours * self.labor_db.get_rate('fitter')
        ))

        # Mano de obra - Campo
        field_hours = (
            self.labor_db.get_operation_hours('erection_simple') +
            self.labor_db.get_operation_hours('bolt_snug') * bolt_count +
            self.labor_db.get_operation_hours('alignment')
        )
        labor.append(LaborCost(
            'Field erection', field_hours,
            self.labor_db.get_rate('ironworker'),
            field_hours * self.labor_db.get_rate('ironworker')
        ))

        return self._compile_breakdown(materials, labor, 'shear_tab')

    def calculate_end_plate_cost(self, config):
        """Calcula costo de conexion end plate."""
        materials = []
        labor = []

        is_extended = config.get('extended', False)
        plate_type = 'Extended end plate' if is_extended else 'End plate'

        # Placa
        plate_weight, plate_cost = self.plate_calc.calculate_plate_cost(
            config.get('plate_length', 400),
            config.get('plate_width', 200),
            config.get('plate_thickness', 20),
            config.get('material', 'A36')
        )
        materials.append(MaterialCost(
            plate_type, plate_weight, 'kg',
            self.material_db.get_steel_price(config.get('material', 'A36')),
            plate_cost
        ))

        # Tornillos (mas en extended)
        bolt_count = config.get('bolt_count', 8 if is_extended else 4)
        bolt_diam = config.get('bolt_diameter', 25)
        bolt_grade = config.get('bolt_grade', 'A490')
        bolt_cost = self.bolt_calc.calculate_bolt_cost(
            bolt_count, bolt_diam, bolt_grade
        )
        materials.append(MaterialCost(
            f'Bolts {bolt_grade} {bolt_diam}mm', bolt_count, 'pcs',
            self.material_db.get_bolt_set_price(bolt_grade, bolt_diam),
            bolt_cost
        ))

        # Soldadura CJP a vigas
        beam_flange_width = config.get('beam_flange_width', 200)
        beam_web_depth = config.get('beam_web_depth', 300)

        # Soldadura flanges (CJP)
        flange_weld_weight, flange_weld_cost = self.weld_calc.calculate_weld_cost(
            'cjp', beam_flange_width * 2, config.get('beam_flange_thickness', 15)
        )
        materials.append(MaterialCost(
            'CJP weld flanges', flange_weld_weight, 'kg',
            self.material_db.get_weld_price_per_kg('E70'),
            flange_weld_cost
        ))

        # Soldadura web (fillet)
        web_weld_weight, web_weld_cost = self.weld_calc.calculate_weld_cost(
            'fillet', beam_web_depth * 2, 8
        )
        materials.append(MaterialCost(
            'Fillet weld web', web_weld_weight, 'kg',
            self.material_db.get_weld_price_per_kg('E70'),
            web_weld_cost
        ))

        # Mano de obra - Taller
        shop_hours = (
            self.labor_db.get_operation_hours('cut_plate_simple') * 4 +
            self.labor_db.get_operation_hours('drill_hole') * bolt_count +
            self.labor_db.get_operation_hours('fit_plate') +
            self.labor_db.get_operation_hours('weld_cjp_per_inch') * (beam_flange_width * 2 / 25.4) +
            self.labor_db.get_operation_hours('weld_fillet_per_inch') * (beam_web_depth * 2 / 25.4)
        )

        # Factor adicional para extended
        if is_extended:
            shop_hours *= 1.3

        labor.append(LaborCost(
            'Shop fabrication', shop_hours,
            self.labor_db.get_rate('welder_certified'),
            shop_hours * self.labor_db.get_rate('welder_certified')
        ))

        # Mano de obra - Campo
        field_hours = (
            self.labor_db.get_operation_hours('erection_moment') +
            self.labor_db.get_operation_hours('bolt_pretension') * bolt_count +
            self.labor_db.get_operation_hours('alignment')
        )
        labor.append(LaborCost(
            'Field erection', field_hours,
            self.labor_db.get_rate('ironworker'),
            field_hours * self.labor_db.get_rate('ironworker')
        ))

        conn_type = 'extended_end_plate' if is_extended else 'end_plate'
        return self._compile_breakdown(materials, labor, conn_type)

    def calculate_rbs_cost(self, config):
        """Calcula costo de conexion RBS (Reduced Beam Section)."""
        materials = []
        labor = []

        # End plate (base de RBS)
        config['extended'] = True
        base_cost = self.calculate_end_plate_cost(config)

        # Agregar costos adicionales de RBS

        # Corte RBS (2 flanges x 2 lados)
        rbs_cut_hours = self.labor_db.get_operation_hours('cut_rbs') * 4
        labor.append(LaborCost(
            'RBS flange cuts', rbs_cut_hours,
            self.labor_db.get_rate('fitter'),
            rbs_cut_hours * self.labor_db.get_rate('fitter')
        ))

        # Acabado y pulido de cortes
        grinding_hours = 0.5 * 4  # 30 min por corte
        labor.append(LaborCost(
            'RBS grinding/finish', grinding_hours,
            self.labor_db.get_rate('fitter'),
            grinding_hours * self.labor_db.get_rate('fitter')
        ))

        # Inspeccion adicional (NDT requerida)
        inspection_hours = 1.5
        labor.append(LaborCost(
            'NDT inspection', inspection_hours,
            self.labor_db.get_rate('inspector'),
            inspection_hours * self.labor_db.get_rate('inspector')
        ))

        # Compilar todo
        all_materials = list(base_cost.materials) if hasattr(base_cost, 'materials') else []
        all_labor = list(base_cost.labor) if hasattr(base_cost, 'labor') else []
        all_labor.extend(labor)

        return self._compile_breakdown(all_materials, all_labor, 'RBS')

    def calculate_wuf_cost(self, config):
        """Calcula costo de conexion WUF (Welded Unreinforced Flange)."""
        materials = []
        labor = []

        is_welded = config.get('welded_web', True)  # WUF-W vs WUF-B
        conn_name = 'WUF-W' if is_welded else 'WUF-B'

        beam_flange_width = config.get('beam_flange_width', 200)
        beam_flange_thickness = config.get('beam_flange_thickness', 15)
        beam_web_depth = config.get('beam_web_depth', 300)
        column_flange_thickness = config.get('column_flange_thickness', 20)

        # Access holes (copas de acceso)
        access_hole_count = 2
        materials.append(MaterialCost(
            'Access hole preparation', access_hole_count, 'pcs',
            15.00, access_hole_count * 15.00
        ))

        # Backing bars
        backing_bar_weight = 0.3 * beam_flange_width / 1000 * 2  # 2 flanges
        backing_bar_cost = backing_bar_weight * 3.50
        materials.append(MaterialCost(
            'Weld backing bars', backing_bar_weight, 'kg',
            3.50, backing_bar_cost
        ))

        # CJP welds a flanges
        flange_weld_weight, flange_weld_cost = self.weld_calc.calculate_weld_cost(
            'cjp', beam_flange_width * 2, beam_flange_thickness
        )
        materials.append(MaterialCost(
            'CJP weld flanges', flange_weld_weight, 'kg',
            self.material_db.get_weld_price_per_kg('E70'),
            flange_weld_cost
        ))

        if is_welded:
            # WUF-W: soldadura en alma
            web_weld_weight, web_weld_cost = self.weld_calc.calculate_weld_cost(
                'cjp', beam_web_depth, 10
            )
            materials.append(MaterialCost(
                'CJP weld web', web_weld_weight, 'kg',
                self.material_db.get_weld_price_per_kg('E70'),
                web_weld_cost
            ))
        else:
            # WUF-B: shear tab bolted
            bolt_count = config.get('bolt_count', 4)
            bolt_diam = config.get('bolt_diameter', 22)
            bolt_grade = config.get('bolt_grade', 'A325')
            bolt_cost = self.bolt_calc.calculate_bolt_cost(
                bolt_count, bolt_diam, bolt_grade
            )
            materials.append(MaterialCost(
                f'Bolts {bolt_grade} {bolt_diam}mm', bolt_count, 'pcs',
                self.material_db.get_bolt_set_price(bolt_grade, bolt_diam),
                bolt_cost
            ))

            # Shear tab
            tab_weight, tab_cost = self.plate_calc.calculate_plate_cost(
                beam_web_depth - 50, 100, 10
            )
            materials.append(MaterialCost(
                'Shear tab', tab_weight, 'kg',
                self.material_db.get_steel_price('A36'),
                tab_cost
            ))

        # Continuity plates (si se requieren)
        if column_flange_thickness < beam_flange_thickness * 0.6:
            cont_plate_weight, cont_plate_cost = self.plate_calc.calculate_plate_cost(
                config.get('column_depth', 350) - 50,
                config.get('column_width', 350) / 2 - 20,
                beam_flange_thickness,
                'A572_Gr50'
            )
            materials.append(MaterialCost(
                'Continuity plates (4)', cont_plate_weight * 4, 'kg',
                self.material_db.get_steel_price('A572_Gr50'),
                cont_plate_cost * 4
            ))

        # Mano de obra - Taller
        shop_hours = (
            self.labor_db.get_operation_hours('cut_plate_complex') * 2 +  # Access holes
            self.labor_db.get_operation_hours('weld_backing_bar') * 2 +
            self.labor_db.get_operation_hours('weld_cjp_per_inch') * (beam_flange_width * 2 / 25.4)
        )

        if is_welded:
            shop_hours += self.labor_db.get_operation_hours('weld_cjp_per_inch') * (beam_web_depth / 25.4)
        else:
            shop_hours += (
                self.labor_db.get_operation_hours('cut_plate_simple') * 4 +
                self.labor_db.get_operation_hours('drill_hole') * config.get('bolt_count', 4) +
                self.labor_db.get_operation_hours('weld_fillet_per_inch') * (beam_web_depth * 2 / 25.4)
            )

        labor.append(LaborCost(
            'Shop fabrication', shop_hours,
            self.labor_db.get_rate('welder_certified'),
            shop_hours * self.labor_db.get_rate('welder_certified')
        ))

        # Mano de obra - Campo
        field_hours = (
            self.labor_db.get_operation_hours('erection_seismic') +
            self.labor_db.get_operation_hours('alignment') +
            self.labor_db.get_operation_hours('inspection')
        )

        if not is_welded:
            field_hours += self.labor_db.get_operation_hours('bolt_pretension') * config.get('bolt_count', 4)

        labor.append(LaborCost(
            'Field erection', field_hours,
            self.labor_db.get_rate('ironworker'),
            field_hours * self.labor_db.get_rate('ironworker')
        ))

        # Inspeccion NDT
        inspection_hours = 2.0
        labor.append(LaborCost(
            'NDT inspection (UT)', inspection_hours,
            self.labor_db.get_rate('inspector'),
            inspection_hours * self.labor_db.get_rate('inspector')
        ))

        return self._compile_breakdown(materials, labor, conn_name)

    def calculate_stiffener_cost(self, config):
        """Calcula costo adicional de rigidizadores."""
        materials = []
        labor = []

        stiffener_type = config.get('type', 'continuity')

        if stiffener_type == 'continuity':
            # Placas de continuidad (4 piezas tipicamente)
            count = config.get('count', 4)
            plate_weight, plate_cost = self.plate_calc.calculate_plate_cost(
                config.get('length', 150),
                config.get('width', 100),
                config.get('thickness', 15),
                config.get('material', 'A572_Gr50')
            )
            materials.append(MaterialCost(
                f'Continuity plates ({count})', plate_weight * count, 'kg',
                self.material_db.get_steel_price(config.get('material', 'A572_Gr50')),
                plate_cost * count
            ))

            # Soldadura
            weld_length = config.get('length', 150) * 4 * count  # 4 lados por placa
            weld_weight, weld_cost = self.weld_calc.calculate_weld_cost(
                'fillet', weld_length, 8
            )
            materials.append(MaterialCost(
                'Fillet weld stiffeners', weld_weight, 'kg',
                self.material_db.get_weld_price_per_kg('E70'),
                weld_cost
            ))

        elif stiffener_type == 'doubler':
            # Placa de refuerzo de alma
            plate_weight, plate_cost = self.plate_calc.calculate_plate_cost(
                config.get('length', 400),
                config.get('width', 300),
                config.get('thickness', 12),
                config.get('material', 'A572_Gr50')
            )
            materials.append(MaterialCost(
                'Doubler plate', plate_weight, 'kg',
                self.material_db.get_steel_price(config.get('material', 'A572_Gr50')),
                plate_cost
            ))

            # Soldadura perimetral PJP + fillet
            perimeter = 2 * (config.get('length', 400) + config.get('width', 300))
            weld_weight, weld_cost = self.weld_calc.calculate_weld_cost(
                'fillet', perimeter, 6
            )
            materials.append(MaterialCost(
                'Perimeter weld doubler', weld_weight, 'kg',
                self.material_db.get_weld_price_per_kg('E70'),
                weld_cost
            ))

        # Mano de obra
        shop_hours = (
            self.labor_db.get_operation_hours('cut_plate_simple') * 4 +
            self.labor_db.get_operation_hours('fit_stiffener') * config.get('count', 4) +
            self.labor_db.get_operation_hours('weld_fillet_per_inch') * 20
        )
        labor.append(LaborCost(
            'Stiffener fabrication', shop_hours,
            self.labor_db.get_rate('welder_standard'),
            shop_hours * self.labor_db.get_rate('welder_standard')
        ))

        return self._compile_breakdown(materials, labor, 'stiffeners')

    def _compile_breakdown(self, materials, labor, connection_type):
        """Compila desglose final de costos."""
        # Totales parciales
        material_total = sum(m.total for m in materials)
        labor_total = sum(l.total for l in labor)

        # Equipo (% de mano de obra)
        equipment = labor_total * 0.15

        # Overhead (gastos generales)
        overhead_rate = 0.20
        overhead = (material_total + labor_total + equipment) * overhead_rate

        # Subtotal
        subtotal = material_total + labor_total + equipment + overhead

        # Factor de complejidad
        complexity = self.COMPLEXITY_FACTORS.get(connection_type, 1.0)
        subtotal *= complexity

        # Contingencia
        contingency_rate = 0.10
        contingency = subtotal * contingency_rate

        # Total
        total = subtotal + contingency

        return CostBreakdown(
            materials=materials,
            labor=labor,
            equipment=equipment,
            overhead=overhead,
            subtotal=subtotal,
            contingency=contingency,
            total=total
        )

    def calculate_connection_cost(self, connection_type, config):
        """
        Calcula costo de conexion segun tipo.

        Args:
            connection_type: Tipo de conexion
            config: Diccionario de configuracion

        Returns:
            CostBreakdown: Desglose de costos
        """
        calculators = {
            'shear_tab': self.calculate_shear_tab_cost,
            'clip_angle': self.calculate_shear_tab_cost,  # Similar
            'end_plate': self.calculate_end_plate_cost,
            'extended_end_plate': lambda c: self.calculate_end_plate_cost({**c, 'extended': True}),
            'RBS': self.calculate_rbs_cost,
            'WUF-W': lambda c: self.calculate_wuf_cost({**c, 'welded_web': True}),
            'WUF-B': lambda c: self.calculate_wuf_cost({**c, 'welded_web': False}),
        }

        calculator = calculators.get(connection_type, self.calculate_shear_tab_cost)
        return calculator(config)

    def generate_cost_report(self, connection_type, config):
        """
        Genera reporte de costos formateado.

        Args:
            connection_type: Tipo de conexion
            config: Configuracion

        Returns:
            str: Reporte formateado
        """
        breakdown = self.calculate_connection_cost(connection_type, config)

        lines = []
        lines.append("=" * 60)
        lines.append(f"REPORTE DE COSTOS - {connection_type.upper()}")
        lines.append("=" * 60)
        lines.append("")

        # Materiales
        lines.append("MATERIALES")
        lines.append("-" * 40)
        for mat in breakdown.materials:
            lines.append(f"  {mat.item:<25} {mat.quantity:>8.2f} {mat.unit:<4} @ ${mat.unit_price:>7.2f} = ${mat.total:>10.2f}")
        material_total = sum(m.total for m in breakdown.materials)
        lines.append(f"  {'Subtotal Materiales':<25} {'':<13} ${material_total:>10.2f}")
        lines.append("")

        # Mano de obra
        lines.append("MANO DE OBRA")
        lines.append("-" * 40)
        for lab in breakdown.labor:
            lines.append(f"  {lab.operation:<25} {lab.hours:>8.2f} hrs @ ${lab.rate:>7.2f} = ${lab.total:>10.2f}")
        labor_total = sum(l.total for l in breakdown.labor)
        lines.append(f"  {'Subtotal Mano de Obra':<25} {'':<13} ${labor_total:>10.2f}")
        lines.append("")

        # Resumen
        lines.append("RESUMEN")
        lines.append("-" * 40)
        lines.append(f"  {'Materiales':<35} ${material_total:>10.2f}")
        lines.append(f"  {'Mano de obra':<35} ${labor_total:>10.2f}")
        lines.append(f"  {'Equipo (15%)':<35} ${breakdown.equipment:>10.2f}")
        lines.append(f"  {'Gastos generales (20%)':<35} ${breakdown.overhead:>10.2f}")
        lines.append(f"  {'Subtotal':<35} ${breakdown.subtotal:>10.2f}")
        lines.append(f"  {'Contingencia (10%)':<35} ${breakdown.contingency:>10.2f}")
        lines.append("-" * 50)
        lines.append(f"  {'TOTAL':<35} ${breakdown.total:>10.2f}")
        lines.append("=" * 60)

        return "\n".join(lines)


class ProjectCostEstimator:
    """Estimador de costos a nivel de proyecto."""

    def __init__(self):
        self.calculator = ConnectionCostCalculator()

    def estimate_project(self, connections):
        """
        Estima costos totales del proyecto.

        Args:
            connections: Lista de dict con:
                - type: Tipo de conexion
                - count: Cantidad
                - config: Configuracion

        Returns:
            dict: Resumen de costos del proyecto
        """
        total_cost = 0.0
        connection_costs = []

        for conn in connections:
            conn_type = conn['type']
            count = conn.get('count', 1)
            config = conn.get('config', {})

            breakdown = self.calculator.calculate_connection_cost(conn_type, config)
            unit_cost = breakdown.total
            subtotal = unit_cost * count

            connection_costs.append({
                'type': conn_type,
                'count': count,
                'unit_cost': unit_cost,
                'subtotal': subtotal
            })

            total_cost += subtotal

        # Factores de proyecto
        mobilization = total_cost * 0.05
        engineering = total_cost * 0.08
        testing = total_cost * 0.03

        project_total = total_cost + mobilization + engineering + testing

        return {
            'connections': connection_costs,
            'direct_cost': total_cost,
            'mobilization': mobilization,
            'engineering': engineering,
            'testing': testing,
            'project_total': project_total
        }


# Ejemplo de uso
if __name__ == "__main__":
    calculator = ConnectionCostCalculator()

    # Ejemplo: Conexion shear tab
    shear_config = {
        'plate_length': 300,
        'plate_width': 100,
        'plate_thickness': 10,
        'bolt_count': 3,
        'bolt_diameter': 22,
        'bolt_grade': 'A325',
        'weld_length': 300,
        'weld_size': 8,
        'material': 'A36'
    }

    report = calculator.generate_cost_report('shear_tab', shear_config)
    print(report)

    print("\n")

    # Ejemplo: Conexion RBS sismica
    rbs_config = {
        'plate_length': 500,
        'plate_width': 250,
        'plate_thickness': 25,
        'bolt_count': 8,
        'bolt_diameter': 25,
        'bolt_grade': 'A490',
        'beam_flange_width': 200,
        'beam_flange_thickness': 15,
        'beam_web_depth': 350,
        'material': 'A572_Gr50'
    }

    report = calculator.generate_cost_report('RBS', rbs_config)
    print(report)
