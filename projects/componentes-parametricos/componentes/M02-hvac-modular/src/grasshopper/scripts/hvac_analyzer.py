#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HVAC Analyzer - M02 HVAC Modular
Analizador de sistemas HVAC: caida de presion, balanceo, costos

Clases principales:
- PressureDropCalculator: Calculos de perdida de presion
- CFMBalancer: Balanceo de caudales
- SystemAnalyzer: Analisis integral del sistema
- HVACCostEstimator: Estimacion de costos
- ReportGenerator: Generador de reportes
"""

import math
from collections import namedtuple

# Estructuras de datos
PressureResult = namedtuple('PressureResult', [
    'segment_id', 'length_m', 'velocity_mps', 'friction_pa_m',
    'fittings_pa', 'total_pa'
])

BalanceResult = namedtuple('BalanceResult', [
    'zone_id', 'design_cfm', 'actual_cfm', 'deviation_pct', 'status'
])

CostBreakdown = namedtuple('CostBreakdown', [
    'ductwork', 'insulation', 'equipment', 'terminals',
    'accessories', 'installation', 'total'
])


class PressureDropCalculator:
    """Calculador de caida de presion en ductos."""

    # Constantes fisicas
    AIR_DENSITY = 1.2  # kg/m3 a condiciones estandar
    AIR_VISCOSITY = 1.81e-5  # Pa.s
    DUCT_ROUGHNESS = 0.0003  # m para ducto galvanizado

    # Coeficientes de perdida local (K factors)
    K_FACTORS = {
        'elbow_90_rect': 0.22,
        'elbow_90_round': 0.15,
        'elbow_45': 0.10,
        'tee_branch': 1.00,
        'tee_main': 0.30,
        'reducer': 0.04,
        'transition': 0.10,
        'damper_open': 0.20,
        'damper_half': 2.50,
        'fire_damper': 0.15,
        'flex_connection': 0.25,
        'diffuser': 0.50,
        'grille': 0.40,
        'filter_clean': 0.50,
        'filter_dirty': 1.50,
        'coil_4row': 0.80,
        'coil_6row': 1.20,
    }

    def __init__(self):
        """Inicializa calculador."""
        self.segments = []
        self.fittings = []

    def add_duct_segment(self, segment_id, length_m, width_mm, height_mm,
                         cfm, is_round=False):
        """
        Agrega segmento de ducto.

        Args:
            segment_id: Identificador del segmento
            length_m: Longitud en metros
            width_mm: Ancho en mm (o diametro si es redondo)
            height_mm: Alto en mm (ignorado si es redondo)
            cfm: Flujo en CFM
            is_round: Si es ducto circular
        """
        segment = {
            'id': segment_id,
            'length': length_m,
            'width': width_mm / 1000.0,
            'height': height_mm / 1000.0,
            'cfm': cfm,
            'is_round': is_round,
            'fittings': []
        }

        # Calcular diametro hidraulico
        if is_round:
            segment['dh'] = width_mm / 1000.0
            segment['area'] = math.pi * (segment['dh'] / 2) ** 2
        else:
            w = segment['width']
            h = segment['height']
            segment['area'] = w * h
            segment['dh'] = 4 * segment['area'] / (2 * (w + h))

        self.segments.append(segment)
        return len(self.segments) - 1

    def add_fitting(self, segment_index, fitting_type, quantity=1):
        """
        Agrega accesorio a un segmento.

        Args:
            segment_index: Indice del segmento
            fitting_type: Tipo de accesorio (ver K_FACTORS)
            quantity: Cantidad
        """
        if 0 <= segment_index < len(self.segments):
            self.segments[segment_index]['fittings'].append({
                'type': fitting_type,
                'quantity': quantity
            })

    def calculate_friction_factor(self, reynolds, relative_roughness):
        """
        Calcula factor de friccion usando Colebrook-White.

        Args:
            reynolds: Numero de Reynolds
            relative_roughness: Rugosidad relativa (e/D)

        Returns:
            Factor de friccion de Darcy
        """
        if reynolds < 2300:
            # Flujo laminar
            return 64.0 / reynolds

        # Flujo turbulento - iteracion de Colebrook-White
        f = 0.02  # Valor inicial

        for _ in range(50):
            term1 = relative_roughness / 3.7
            term2 = 2.51 / (reynolds * math.sqrt(f))
            f_new = 1.0 / (-2.0 * math.log10(term1 + term2)) ** 2

            if abs(f_new - f) < 1e-8:
                break
            f = f_new

        return f

    def calculate_segment_pressure_drop(self, segment):
        """
        Calcula caida de presion de un segmento.

        Args:
            segment: Diccionario de segmento

        Returns:
            PressureResult
        """
        # Convertir CFM a m3/s
        flow_m3s = segment['cfm'] * 0.000471947

        # Velocidad
        velocity = flow_m3s / segment['area']

        # Numero de Reynolds
        reynolds = (self.AIR_DENSITY * velocity * segment['dh']) / self.AIR_VISCOSITY

        # Factor de friccion
        relative_roughness = self.DUCT_ROUGHNESS / segment['dh']
        friction_factor = self.calculate_friction_factor(reynolds, relative_roughness)

        # Perdida por friccion (Pa/m)
        friction_loss_per_m = (friction_factor * self.AIR_DENSITY *
                               velocity ** 2 / (2 * segment['dh']))

        # Perdida total por friccion
        friction_loss_total = friction_loss_per_m * segment['length']

        # Perdidas locales (accesorios)
        fitting_loss = 0.0
        dynamic_pressure = 0.5 * self.AIR_DENSITY * velocity ** 2

        for fitting in segment['fittings']:
            k_factor = self.K_FACTORS.get(fitting['type'], 0.5)
            fitting_loss += k_factor * dynamic_pressure * fitting['quantity']

        # Total
        total_loss = friction_loss_total + fitting_loss

        return PressureResult(
            segment_id=segment['id'],
            length_m=segment['length'],
            velocity_mps=velocity,
            friction_pa_m=friction_loss_per_m,
            fittings_pa=fitting_loss,
            total_pa=total_loss
        )

    def calculate_system_pressure_drop(self):
        """
        Calcula caida de presion total del sistema.

        Returns:
            Diccionario con resultados del sistema
        """
        results = []
        total_pressure = 0.0
        critical_path = []

        for segment in self.segments:
            result = self.calculate_segment_pressure_drop(segment)
            results.append(result)
            total_pressure += result.total_pa

        # Encontrar ruta critica (maxima caida de presion)
        max_pressure = 0
        for result in results:
            if result.total_pa > max_pressure:
                max_pressure = result.total_pa
                critical_path = [result.segment_id]

        return {
            'segment_results': results,
            'total_pressure_drop_pa': total_pressure,
            'critical_path': critical_path,
            'max_velocity_mps': max(r.velocity_mps for r in results) if results else 0
        }


class CFMBalancer:
    """Balanceador de caudales de aire."""

    # Tolerancias ASHRAE
    TOLERANCE_SUPPLY = 0.10  # +-10% para suministro
    TOLERANCE_RETURN = 0.10  # +-10% para retorno
    TOLERANCE_EXHAUST = 0.10  # +-10% para extraccion

    def __init__(self):
        """Inicializa balanceador."""
        self.zones = []
        self.supply_total = 0
        self.return_total = 0
        self.exhaust_total = 0

    def add_zone(self, zone_id, zone_name, design_supply_cfm,
                 design_return_cfm=None, design_exhaust_cfm=0):
        """
        Agrega zona al sistema.

        Args:
            zone_id: Identificador de zona
            zone_name: Nombre de zona
            design_supply_cfm: CFM de suministro de diseno
            design_return_cfm: CFM de retorno (default = supply - exhaust)
            design_exhaust_cfm: CFM de extraccion
        """
        if design_return_cfm is None:
            design_return_cfm = design_supply_cfm - design_exhaust_cfm

        zone = {
            'id': zone_id,
            'name': zone_name,
            'design_supply': design_supply_cfm,
            'design_return': design_return_cfm,
            'design_exhaust': design_exhaust_cfm,
            'actual_supply': None,
            'actual_return': None,
            'actual_exhaust': None
        }

        self.zones.append(zone)
        self.supply_total += design_supply_cfm
        self.return_total += design_return_cfm
        self.exhaust_total += design_exhaust_cfm

    def set_actual_values(self, zone_id, actual_supply=None,
                          actual_return=None, actual_exhaust=None):
        """
        Establece valores reales medidos.

        Args:
            zone_id: Identificador de zona
            actual_supply: CFM suministro real
            actual_return: CFM retorno real
            actual_exhaust: CFM extraccion real
        """
        for zone in self.zones:
            if zone['id'] == zone_id:
                if actual_supply is not None:
                    zone['actual_supply'] = actual_supply
                if actual_return is not None:
                    zone['actual_return'] = actual_return
                if actual_exhaust is not None:
                    zone['actual_exhaust'] = actual_exhaust
                break

    def check_zone_balance(self, zone):
        """
        Verifica balance de una zona.

        Args:
            zone: Diccionario de zona

        Returns:
            Lista de BalanceResult
        """
        results = []

        # Verificar suministro
        if zone['actual_supply'] is not None:
            design = zone['design_supply']
            actual = zone['actual_supply']
            deviation = (actual - design) / design * 100 if design > 0 else 0

            status = 'OK' if abs(deviation) <= self.TOLERANCE_SUPPLY * 100 else 'ADJUST'

            results.append(BalanceResult(
                zone_id=zone['id'],
                design_cfm=design,
                actual_cfm=actual,
                deviation_pct=deviation,
                status=f'SUPPLY: {status}'
            ))

        # Verificar retorno
        if zone['actual_return'] is not None:
            design = zone['design_return']
            actual = zone['actual_return']
            deviation = (actual - design) / design * 100 if design > 0 else 0

            status = 'OK' if abs(deviation) <= self.TOLERANCE_RETURN * 100 else 'ADJUST'

            results.append(BalanceResult(
                zone_id=zone['id'],
                design_cfm=design,
                actual_cfm=actual,
                deviation_pct=deviation,
                status=f'RETURN: {status}'
            ))

        # Verificar extraccion
        if zone['actual_exhaust'] is not None and zone['design_exhaust'] > 0:
            design = zone['design_exhaust']
            actual = zone['actual_exhaust']
            deviation = (actual - design) / design * 100 if design > 0 else 0

            status = 'OK' if abs(deviation) <= self.TOLERANCE_EXHAUST * 100 else 'ADJUST'

            results.append(BalanceResult(
                zone_id=zone['id'],
                design_cfm=design,
                actual_cfm=actual,
                deviation_pct=deviation,
                status=f'EXHAUST: {status}'
            ))

        return results

    def calculate_system_balance(self):
        """
        Calcula balance general del sistema.

        Returns:
            Diccionario con resultados del balance
        """
        zone_results = []
        issues = []

        for zone in self.zones:
            zone_balance = self.check_zone_balance(zone)
            zone_results.extend(zone_balance)

            for result in zone_balance:
                if 'ADJUST' in result.status:
                    issues.append({
                        'zone': zone['id'],
                        'issue': result.status,
                        'deviation': result.deviation_pct
                    })

        # Totales
        actual_supply = sum(z['actual_supply'] or z['design_supply']
                           for z in self.zones)
        actual_return = sum(z['actual_return'] or z['design_return']
                           for z in self.zones)
        actual_exhaust = sum(z['actual_exhaust'] or z['design_exhaust']
                            for z in self.zones)

        # Presion del edificio
        building_cfm_delta = actual_supply - actual_return - actual_exhaust
        building_pressure = 'POSITIVE' if building_cfm_delta > 0 else 'NEGATIVE'

        return {
            'zone_results': zone_results,
            'issues': issues,
            'total_supply_cfm': actual_supply,
            'total_return_cfm': actual_return,
            'total_exhaust_cfm': actual_exhaust,
            'building_cfm_delta': building_cfm_delta,
            'building_pressure': building_pressure,
            'balance_status': 'OK' if len(issues) == 0 else 'NEEDS_ADJUSTMENT'
        }


class SystemAnalyzer:
    """Analizador integral de sistema HVAC."""

    # Parametros de diseno
    DESIGN_PARAMS = {
        'max_supply_velocity_mps': 10.0,
        'max_return_velocity_mps': 8.0,
        'max_branch_velocity_mps': 6.0,
        'max_pressure_drop_pa_m': 1.5,
        'min_outdoor_air_pct': 15.0,
        'max_nc_level': 35,
    }

    def __init__(self):
        """Inicializa analizador."""
        self.pressure_calc = PressureDropCalculator()
        self.cfm_balancer = CFMBalancer()
        self.equipment = []

    def add_equipment(self, equip_id, equip_type, capacity_cfm,
                      static_pressure_pa, motor_hp):
        """
        Agrega equipo al sistema.

        Args:
            equip_id: Identificador del equipo
            equip_type: Tipo ('ahu', 'vav', 'fan_coil', etc.)
            capacity_cfm: Capacidad en CFM
            static_pressure_pa: Presion estatica disponible
            motor_hp: Potencia del motor
        """
        self.equipment.append({
            'id': equip_id,
            'type': equip_type,
            'capacity_cfm': capacity_cfm,
            'static_pressure': static_pressure_pa,
            'motor_hp': motor_hp
        })

    def analyze_system(self):
        """
        Realiza analisis completo del sistema.

        Returns:
            Diccionario con resultados del analisis
        """
        results = {
            'pressure_analysis': None,
            'balance_analysis': None,
            'equipment_analysis': [],
            'compliance': [],
            'recommendations': []
        }

        # Analisis de presion
        pressure_results = self.pressure_calc.calculate_system_pressure_drop()
        results['pressure_analysis'] = pressure_results

        # Verificar velocidades
        for seg_result in pressure_results['segment_results']:
            if seg_result.velocity_mps > self.DESIGN_PARAMS['max_supply_velocity_mps']:
                results['recommendations'].append({
                    'segment': seg_result.segment_id,
                    'issue': 'HIGH_VELOCITY',
                    'value': seg_result.velocity_mps,
                    'max_allowed': self.DESIGN_PARAMS['max_supply_velocity_mps'],
                    'action': 'Increase duct size or reduce airflow'
                })

        # Analisis de balance
        balance_results = self.cfm_balancer.calculate_system_balance()
        results['balance_analysis'] = balance_results

        # Analisis de equipos
        total_pressure_required = pressure_results['total_pressure_drop_pa']

        for equip in self.equipment:
            equip_analysis = {
                'id': equip['id'],
                'type': equip['type'],
                'capacity': equip['capacity_cfm'],
                'static_available': equip['static_pressure'],
                'static_required': total_pressure_required,
                'margin': equip['static_pressure'] - total_pressure_required
            }

            if equip_analysis['margin'] < 0:
                equip_analysis['status'] = 'INSUFFICIENT_PRESSURE'
                results['recommendations'].append({
                    'equipment': equip['id'],
                    'issue': 'INSUFFICIENT_STATIC_PRESSURE',
                    'deficit_pa': abs(equip_analysis['margin']),
                    'action': 'Upgrade fan or reduce system resistance'
                })
            elif equip_analysis['margin'] < total_pressure_required * 0.1:
                equip_analysis['status'] = 'LOW_MARGIN'
            else:
                equip_analysis['status'] = 'OK'

            results['equipment_analysis'].append(equip_analysis)

        return results

    def generate_compliance_report(self, code='ASHRAE'):
        """
        Genera reporte de cumplimiento de codigo.

        Args:
            code: Codigo de referencia ('ASHRAE', 'IMC', 'UMC')

        Returns:
            Lista de items de cumplimiento
        """
        compliance = []

        # Verificar aire exterior minimo
        total_supply = self.cfm_balancer.supply_total
        outdoor_air_min = total_supply * self.DESIGN_PARAMS['min_outdoor_air_pct'] / 100

        compliance.append({
            'requirement': f'{code} 62.1 - Minimum Outdoor Air',
            'minimum': outdoor_air_min,
            'status': 'VERIFY',
            'notes': f'Verify {outdoor_air_min:.0f} CFM outdoor air provided'
        })

        # Verificar niveles de ruido
        compliance.append({
            'requirement': f'{code} - Noise Criteria',
            'maximum_nc': self.DESIGN_PARAMS['max_nc_level'],
            'status': 'VERIFY',
            'notes': 'Verify NC levels at diffusers'
        })

        # Verificar acceso para mantenimiento
        compliance.append({
            'requirement': f'{code} - Maintenance Access',
            'status': 'VERIFY',
            'notes': 'Verify access panels at all dampers, coils, filters'
        })

        return compliance


class HVACCostEstimator:
    """Estimador de costos de sistema HVAC."""

    # Costos unitarios (USD)
    UNIT_COSTS = {
        # Ductos (por m2 de area superficial)
        'duct_galv_rect': 45.0,
        'duct_galv_round': 38.0,
        'duct_ss_rect': 125.0,
        'duct_aluminum': 85.0,

        # Aislamiento (por m2)
        'insulation_25mm': 18.0,
        'insulation_50mm': 28.0,
        'insulation_75mm': 42.0,

        # Accesorios
        'elbow_90_small': 25.0,
        'elbow_90_medium': 45.0,
        'elbow_90_large': 85.0,
        'tee_small': 35.0,
        'tee_medium': 65.0,
        'tee_large': 120.0,
        'damper_small': 85.0,
        'damper_medium': 145.0,
        'damper_large': 280.0,
        'fire_damper': 450.0,

        # Difusores y rejillas
        'diffuser_6x6': 45.0,
        'diffuser_12x12': 85.0,
        'diffuser_24x24': 165.0,
        'grille_small': 35.0,
        'grille_medium': 65.0,
        'grille_large': 95.0,
        'linear_slot_ft': 55.0,

        # Equipos (por tonelada o CFM)
        'ahu_per_cfm': 3.50,
        'vav_box_small': 650.0,
        'vav_box_medium': 950.0,
        'vav_box_large': 1450.0,
        'fan_coil_per_cfm': 1.80,

        # Instalacion (factor multiplicador)
        'installation_factor': 0.65,
    }

    def __init__(self):
        """Inicializa estimador."""
        self.ductwork_items = []
        self.insulation_items = []
        self.equipment_items = []
        self.terminal_items = []
        self.accessory_items = []

    def add_ductwork(self, description, area_m2, duct_type='duct_galv_rect'):
        """Agrega item de ducto."""
        unit_cost = self.UNIT_COSTS.get(duct_type, 45.0)
        self.ductwork_items.append({
            'description': description,
            'quantity': area_m2,
            'unit': 'm2',
            'unit_cost': unit_cost,
            'total': area_m2 * unit_cost
        })

    def add_insulation(self, description, area_m2, thickness_mm=50):
        """Agrega item de aislamiento."""
        if thickness_mm <= 25:
            key = 'insulation_25mm'
        elif thickness_mm <= 50:
            key = 'insulation_50mm'
        else:
            key = 'insulation_75mm'

        unit_cost = self.UNIT_COSTS[key]
        self.insulation_items.append({
            'description': description,
            'quantity': area_m2,
            'unit': 'm2',
            'unit_cost': unit_cost,
            'total': area_m2 * unit_cost
        })

    def add_equipment(self, description, equip_type, capacity, quantity=1):
        """Agrega item de equipo."""
        if equip_type == 'ahu':
            unit_cost = capacity * self.UNIT_COSTS['ahu_per_cfm']
        elif equip_type == 'vav':
            if capacity <= 500:
                unit_cost = self.UNIT_COSTS['vav_box_small']
            elif capacity <= 1500:
                unit_cost = self.UNIT_COSTS['vav_box_medium']
            else:
                unit_cost = self.UNIT_COSTS['vav_box_large']
        elif equip_type == 'fan_coil':
            unit_cost = capacity * self.UNIT_COSTS['fan_coil_per_cfm']
        else:
            unit_cost = 1000.0

        self.equipment_items.append({
            'description': description,
            'quantity': quantity,
            'unit': 'ea',
            'unit_cost': unit_cost,
            'total': quantity * unit_cost
        })

    def add_terminal(self, description, terminal_type, size, quantity=1):
        """Agrega item de terminal."""
        # Determinar costo basado en tamano
        if 'diffuser' in terminal_type.lower():
            if size <= 8:
                key = 'diffuser_6x6'
            elif size <= 16:
                key = 'diffuser_12x12'
            else:
                key = 'diffuser_24x24'
        elif 'grille' in terminal_type.lower():
            if size <= 10:
                key = 'grille_small'
            elif size <= 18:
                key = 'grille_medium'
            else:
                key = 'grille_large'
        else:
            key = 'diffuser_12x12'

        unit_cost = self.UNIT_COSTS[key]
        self.terminal_items.append({
            'description': description,
            'quantity': quantity,
            'unit': 'ea',
            'unit_cost': unit_cost,
            'total': quantity * unit_cost
        })

    def add_accessory(self, description, accessory_type, quantity=1):
        """Agrega accesorio."""
        unit_cost = self.UNIT_COSTS.get(accessory_type, 50.0)
        self.accessory_items.append({
            'description': description,
            'quantity': quantity,
            'unit': 'ea',
            'unit_cost': unit_cost,
            'total': quantity * unit_cost
        })

    def calculate_total(self):
        """
        Calcula costo total del sistema.

        Returns:
            CostBreakdown
        """
        ductwork_total = sum(item['total'] for item in self.ductwork_items)
        insulation_total = sum(item['total'] for item in self.insulation_items)
        equipment_total = sum(item['total'] for item in self.equipment_items)
        terminals_total = sum(item['total'] for item in self.terminal_items)
        accessories_total = sum(item['total'] for item in self.accessory_items)

        subtotal = (ductwork_total + insulation_total + equipment_total +
                   terminals_total + accessories_total)

        installation = subtotal * self.UNIT_COSTS['installation_factor']
        total = subtotal + installation

        return CostBreakdown(
            ductwork=ductwork_total,
            insulation=insulation_total,
            equipment=equipment_total,
            terminals=terminals_total,
            accessories=accessories_total,
            installation=installation,
            total=total
        )

    def generate_estimate_report(self):
        """
        Genera reporte detallado de estimacion.

        Returns:
            Diccionario con reporte completo
        """
        breakdown = self.calculate_total()

        return {
            'ductwork': {
                'items': self.ductwork_items,
                'subtotal': breakdown.ductwork
            },
            'insulation': {
                'items': self.insulation_items,
                'subtotal': breakdown.insulation
            },
            'equipment': {
                'items': self.equipment_items,
                'subtotal': breakdown.equipment
            },
            'terminals': {
                'items': self.terminal_items,
                'subtotal': breakdown.terminals
            },
            'accessories': {
                'items': self.accessory_items,
                'subtotal': breakdown.accessories
            },
            'installation': breakdown.installation,
            'grand_total': breakdown.total
        }


class ReportGenerator:
    """Generador de reportes de sistema HVAC."""

    def __init__(self, project_name, system_name):
        """
        Inicializa generador de reportes.

        Args:
            project_name: Nombre del proyecto
            system_name: Nombre del sistema
        """
        self.project_name = project_name
        self.system_name = system_name

    def generate_summary_report(self, analyzer, cost_estimator):
        """
        Genera reporte resumen.

        Args:
            analyzer: SystemAnalyzer con analisis completado
            cost_estimator: HVACCostEstimator con estimacion

        Returns:
            Diccionario con reporte completo
        """
        analysis = analyzer.analyze_system()
        costs = cost_estimator.calculate_total()
        compliance = analyzer.generate_compliance_report()

        report = {
            'header': {
                'project': self.project_name,
                'system': self.system_name,
                'date': 'CURRENT_DATE'
            },
            'system_summary': {
                'total_supply_cfm': analyzer.cfm_balancer.supply_total,
                'total_return_cfm': analyzer.cfm_balancer.return_total,
                'total_exhaust_cfm': analyzer.cfm_balancer.exhaust_total,
                'total_pressure_drop_pa': analysis['pressure_analysis']['total_pressure_drop_pa'],
                'equipment_count': len(analyzer.equipment),
                'zone_count': len(analyzer.cfm_balancer.zones)
            },
            'pressure_analysis': {
                'total_drop_pa': analysis['pressure_analysis']['total_pressure_drop_pa'],
                'max_velocity_mps': analysis['pressure_analysis']['max_velocity_mps'],
                'critical_path': analysis['pressure_analysis']['critical_path']
            },
            'balance_status': analysis['balance_analysis']['balance_status'],
            'equipment_status': [
                {
                    'id': eq['id'],
                    'status': eq['status'],
                    'margin_pa': eq['margin']
                }
                for eq in analysis['equipment_analysis']
            ],
            'cost_summary': {
                'ductwork': costs.ductwork,
                'insulation': costs.insulation,
                'equipment': costs.equipment,
                'terminals': costs.terminals,
                'accessories': costs.accessories,
                'installation': costs.installation,
                'total': costs.total
            },
            'compliance': compliance,
            'recommendations': analysis['recommendations']
        }

        return report

    def format_text_report(self, report_data):
        """
        Formatea reporte como texto.

        Args:
            report_data: Diccionario de reporte

        Returns:
            String con reporte formateado
        """
        lines = []

        # Encabezado
        lines.append('=' * 60)
        lines.append(f"HVAC SYSTEM ANALYSIS REPORT")
        lines.append(f"Project: {report_data['header']['project']}")
        lines.append(f"System: {report_data['header']['system']}")
        lines.append('=' * 60)
        lines.append('')

        # Resumen del sistema
        lines.append('SYSTEM SUMMARY')
        lines.append('-' * 40)
        summary = report_data['system_summary']
        lines.append(f"Total Supply CFM: {summary['total_supply_cfm']:,.0f}")
        lines.append(f"Total Return CFM: {summary['total_return_cfm']:,.0f}")
        lines.append(f"Total Exhaust CFM: {summary['total_exhaust_cfm']:,.0f}")
        lines.append(f"System Pressure Drop: {summary['total_pressure_drop_pa']:.1f} Pa")
        lines.append(f"Equipment Count: {summary['equipment_count']}")
        lines.append(f"Zone Count: {summary['zone_count']}")
        lines.append('')

        # Analisis de presion
        lines.append('PRESSURE ANALYSIS')
        lines.append('-' * 40)
        pressure = report_data['pressure_analysis']
        lines.append(f"Total Drop: {pressure['total_drop_pa']:.1f} Pa")
        lines.append(f"Max Velocity: {pressure['max_velocity_mps']:.2f} m/s")
        lines.append('')

        # Estado de balance
        lines.append('BALANCE STATUS')
        lines.append('-' * 40)
        lines.append(f"Status: {report_data['balance_status']}")
        lines.append('')

        # Estado de equipos
        lines.append('EQUIPMENT STATUS')
        lines.append('-' * 40)
        for eq in report_data['equipment_status']:
            lines.append(f"  {eq['id']}: {eq['status']} (Margin: {eq['margin_pa']:.0f} Pa)")
        lines.append('')

        # Resumen de costos
        lines.append('COST SUMMARY')
        lines.append('-' * 40)
        costs = report_data['cost_summary']
        lines.append(f"  Ductwork:     ${costs['ductwork']:>12,.2f}")
        lines.append(f"  Insulation:   ${costs['insulation']:>12,.2f}")
        lines.append(f"  Equipment:    ${costs['equipment']:>12,.2f}")
        lines.append(f"  Terminals:    ${costs['terminals']:>12,.2f}")
        lines.append(f"  Accessories:  ${costs['accessories']:>12,.2f}")
        lines.append(f"  Installation: ${costs['installation']:>12,.2f}")
        lines.append('-' * 40)
        lines.append(f"  TOTAL:        ${costs['total']:>12,.2f}")
        lines.append('')

        # Recomendaciones
        if report_data['recommendations']:
            lines.append('RECOMMENDATIONS')
            lines.append('-' * 40)
            for i, rec in enumerate(report_data['recommendations'], 1):
                lines.append(f"  {i}. {rec.get('issue', 'Issue')}")
                lines.append(f"     Action: {rec.get('action', 'Review')}")
            lines.append('')

        lines.append('=' * 60)
        lines.append('END OF REPORT')
        lines.append('=' * 60)

        return '\n'.join(lines)
