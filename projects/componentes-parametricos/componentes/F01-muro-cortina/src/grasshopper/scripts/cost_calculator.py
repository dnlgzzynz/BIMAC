"""
Cost Calculator - Muro Cortina Parametrico
Calcula costos detallados del sistema de muro cortina.

Inputs:
    mullions_data (List[ProfileData]): Datos de mullions
    transoms_data (List[ProfileData]): Datos de travesanos
    panels_data (List[PanelData]): Datos de paneles
    panel_summary (dict): Resumen de paneles
    system_type (str): Tipo de sistema (stick/unitized/structural/point_fixed)
    material_grade (str): Grado de material (basic/standard/premium)

Outputs:
    total_cost (float): Costo total (MXN)
    cost_breakdown (dict): Desglose de costos
    cost_per_m2 (float): Costo por metro cuadrado
    report (str): Reporte de costos formateado
"""

from collections import namedtuple
from enum import Enum

# Resultado de costos
CostBreakdown = namedtuple('CostBreakdown', [
    'category', 'item', 'quantity', 'unit',
    'unit_cost', 'subtotal', 'notes'
])

CostResult = namedtuple('CostResult', [
    'total_cost', 'breakdown', 'cost_per_m2',
    'total_area', 'system_type', 'grade'
])


class MaterialGrade(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class CurtainWallCostDatabase:
    """Base de datos de costos para muro cortina."""

    # Costos base en MXN (2025)
    COSTS = {
        # Perfiles de aluminio (MXN/kg)
        'aluminum': {
            'basic': 85,
            'standard': 120,
            'premium': 180
        },

        # Acabados (MXN/m2 de perfil)
        'finishes': {
            'anodized_natural': 180,
            'anodized_bronze': 250,
            'powder_coat': 320,
            'pvdf': 480,
            'wood_grain': 650
        },

        # Vidrios (MXN/m2)
        'glass': {
            'single_clear': 380,
            'single_tinted': 520,
            'double_clear': 650,
            'double_low_e': 1100,
            'double_low_e_argon': 1350,
            'triple_low_e': 1850,
            'triple_low_e_argon': 2200,
            'laminated_clear': 980,
            'laminated_tinted': 1250
        },

        # Spandrel (MXN/m2)
        'spandrel': {
            'aluminum_composite': 520,
            'insulated_metal': 780,
            'glass_opaque': 950,
            'ceramic_frit': 1350
        },

        # Sellos y empaques (MXN/m)
        'gaskets': {
            'epdm_standard': 45,
            'epdm_thermal': 75,
            'silicone': 120,
            'structural_silicone': 280
        },

        # Selladores (MXN/m)
        'sealants': {
            'silicone_standard': 65,
            'silicone_structural': 180,
            'polyurethane': 95
        },

        # Anclajes (MXN/pieza)
        'anchors': {
            'standard': 280,
            'thermal_break': 450,
            'adjustable': 680,
            'seismic': 950
        },

        # Herrajes (MXN/pieza)
        'hardware': {
            'corner_bracket': 180,
            'transom_clip': 95,
            'pressure_plate': 350,
            'spider_fitting': 2800
        },

        # Mano de obra instalacion (MXN/m2)
        'labor': {
            'stick': {
                'basic': 650,
                'standard': 850,
                'premium': 1100
            },
            'unitized': {
                'basic': 380,
                'standard': 450,
                'premium': 580
            },
            'structural_glazing': {
                'basic': 980,
                'standard': 1200,
                'premium': 1500
            },
            'point_fixed': {
                'basic': 1400,
                'standard': 1800,
                'premium': 2400
            }
        },

        # Factores por tipo de sistema
        'system_factors': {
            'stick': 1.0,
            'unitized': 1.35,
            'structural_glazing': 1.25,
            'point_fixed': 1.80
        },

        # Factores por complejidad geometrica
        'geometry_factors': {
            'planar': 1.0,
            'single_curve': 1.25,
            'double_curve': 1.65,
            'corner': 1.40
        }
    }

    @classmethod
    def get_cost(cls, category, item, grade='standard'):
        """Obtiene costo de la base de datos."""
        if category not in cls.COSTS:
            return 0

        category_data = cls.COSTS[category]

        if isinstance(category_data, dict):
            if item in category_data:
                item_data = category_data[item]
                if isinstance(item_data, dict) and grade in item_data:
                    return item_data[grade]
                return item_data
            elif grade in category_data:
                return category_data[grade]

        return 0


class CurtainWallCostCalculator:
    """Calculadora de costos para muro cortina."""

    def __init__(self, currency='MXN'):
        self.currency = currency
        self.db = CurtainWallCostDatabase()

    def calculate(self, mullions_data, transoms_data, panels_data,
                  panel_summary, system_type='stick', material_grade='standard'):
        """
        Calcula el costo total del muro cortina.

        Args:
            mullions_data: Datos de mullions
            transoms_data: Datos de travesanos
            panels_data: Datos de paneles
            panel_summary: Resumen de paneles
            system_type: Tipo de sistema
            material_grade: Grado de material

        Returns:
            CostResult
        """
        breakdown = []

        # 1. Costo de perfiles de aluminio
        aluminum_cost = self._calculate_aluminum_cost(
            mullions_data, transoms_data, material_grade
        )
        breakdown.extend(aluminum_cost)

        # 2. Costo de acabados
        finish_cost = self._calculate_finish_cost(
            mullions_data, transoms_data, material_grade
        )
        breakdown.extend(finish_cost)

        # 3. Costo de vidrios
        glass_cost = self._calculate_glass_cost(
            panels_data, panel_summary, material_grade
        )
        breakdown.extend(glass_cost)

        # 4. Costo de spandrel
        spandrel_cost = self._calculate_spandrel_cost(
            panels_data, panel_summary, material_grade
        )
        breakdown.extend(spandrel_cost)

        # 5. Costo de sellos y empaques
        gasket_cost = self._calculate_gasket_cost(
            mullions_data, transoms_data, system_type
        )
        breakdown.extend(gasket_cost)

        # 6. Costo de selladores
        sealant_cost = self._calculate_sealant_cost(
            panels_data, system_type
        )
        breakdown.extend(sealant_cost)

        # 7. Costo de anclajes
        anchor_cost = self._calculate_anchor_cost(
            mullions_data, system_type
        )
        breakdown.extend(anchor_cost)

        # 8. Costo de herrajes
        hardware_cost = self._calculate_hardware_cost(
            mullions_data, transoms_data, system_type
        )
        breakdown.extend(hardware_cost)

        # 9. Costo de mano de obra
        labor_cost = self._calculate_labor_cost(
            panel_summary, system_type, material_grade
        )
        breakdown.extend(labor_cost)

        # Calcular totales
        subtotal = sum(item.subtotal for item in breakdown)

        # Aplicar factor de sistema
        system_factor = self.db.COSTS['system_factors'].get(system_type, 1.0)

        # Factor de geometria (basado en paneles curvos)
        curved_percent = panel_summary.get('curved_panels', 0) / max(panel_summary.get('total_panels', 1), 1)
        if curved_percent > 0.3:
            geometry_factor = 1.35
        elif curved_percent > 0.1:
            geometry_factor = 1.15
        else:
            geometry_factor = 1.0

        # 10. Agregar indirectos (15%)
        indirect_cost = subtotal * 0.15
        breakdown.append(CostBreakdown(
            category='Indirectos',
            item='Administracion y utilidad',
            quantity=1,
            unit='global',
            unit_cost=indirect_cost,
            subtotal=indirect_cost,
            notes='15% sobre costo directo'
        ))

        # 11. Agregar contingencia (10%)
        contingency = subtotal * 0.10
        breakdown.append(CostBreakdown(
            category='Contingencia',
            item='Imprevistos',
            quantity=1,
            unit='global',
            unit_cost=contingency,
            subtotal=contingency,
            notes='10% sobre costo directo'
        ))

        # Total
        total_cost = subtotal + indirect_cost + contingency
        total_cost *= geometry_factor

        # Area total
        total_area = panel_summary.get('total_area', 1)

        # Costo por m2
        cost_per_m2 = total_cost / total_area if total_area > 0 else 0

        return CostResult(
            total_cost=total_cost,
            breakdown=breakdown,
            cost_per_m2=cost_per_m2,
            total_area=total_area,
            system_type=system_type,
            grade=material_grade
        )

    def _calculate_aluminum_cost(self, mullions_data, transoms_data, grade):
        """Calcula costo de perfiles de aluminio."""
        items = []

        # Peso total de mullions
        mullion_weight = sum(
            m.weight if hasattr(m, 'weight') else 0
            for m in mullions_data
        )
        if mullion_weight == 0:
            # Estimar: 5 kg/m de perfil
            mullion_length = sum(m.length if hasattr(m, 'length') else 0 for m in mullions_data)
            mullion_weight = mullion_length * 5

        unit_cost = self.db.get_cost('aluminum', grade, grade)
        subtotal = mullion_weight * unit_cost

        items.append(CostBreakdown(
            category='Aluminio',
            item='Perfiles mullion',
            quantity=mullion_weight,
            unit='kg',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes=f'Aluminio grado {grade}'
        ))

        # Peso de travesanos
        transom_weight = sum(
            t.weight if hasattr(t, 'weight') else 0
            for t in transoms_data
        )
        if transom_weight == 0:
            transom_length = sum(t.length if hasattr(t, 'length') else 0 for t in transoms_data)
            transom_weight = transom_length * 3.5

        subtotal_t = transom_weight * unit_cost

        items.append(CostBreakdown(
            category='Aluminio',
            item='Perfiles transom',
            quantity=transom_weight,
            unit='kg',
            unit_cost=unit_cost,
            subtotal=subtotal_t,
            notes=f'Aluminio grado {grade}'
        ))

        return items

    def _calculate_finish_cost(self, mullions_data, transoms_data, grade):
        """Calcula costo de acabados."""
        items = []

        # Mapear grado a acabado
        finish_map = {
            'basic': 'anodized_natural',
            'standard': 'powder_coat',
            'premium': 'pvdf'
        }
        finish_type = finish_map.get(grade, 'powder_coat')

        # Superficie de perfiles (perimetro * longitud)
        # Mullion tipico: perimetro ~0.43m (65+150+65+150 mm)
        mullion_length = sum(m.length if hasattr(m, 'length') else 0 for m in mullions_data)
        mullion_surface = mullion_length * 0.43

        # Transom tipico: perimetro ~0.34m
        transom_length = sum(t.length if hasattr(t, 'length') else 0 for t in transoms_data)
        transom_surface = transom_length * 0.34

        total_surface = mullion_surface + transom_surface
        unit_cost = self.db.get_cost('finishes', finish_type)
        subtotal = total_surface * unit_cost

        items.append(CostBreakdown(
            category='Acabados',
            item=finish_type.replace('_', ' ').title(),
            quantity=total_surface,
            unit='m2',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Superficie de perfiles'
        ))

        return items

    def _calculate_glass_cost(self, panels_data, panel_summary, grade):
        """Calcula costo de vidrios."""
        items = []

        # Mapear grado a tipo de vidrio
        glass_map = {
            'basic': 'double_clear',
            'standard': 'double_low_e',
            'premium': 'triple_low_e_argon'
        }
        glass_type = glass_map.get(grade, 'double_low_e')

        vision_area = panel_summary.get('vision_area', 0)
        unit_cost = self.db.get_cost('glass', glass_type)
        subtotal = vision_area * unit_cost

        items.append(CostBreakdown(
            category='Vidrio',
            item=glass_type.replace('_', ' ').title(),
            quantity=vision_area,
            unit='m2',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Area de vision'
        ))

        return items

    def _calculate_spandrel_cost(self, panels_data, panel_summary, grade):
        """Calcula costo de spandrel."""
        items = []

        spandrel_area = panel_summary.get('spandrel_area', 0)

        if spandrel_area <= 0:
            return items

        # Mapear grado a tipo de spandrel
        spandrel_map = {
            'basic': 'aluminum_composite',
            'standard': 'insulated_metal',
            'premium': 'ceramic_frit'
        }
        spandrel_type = spandrel_map.get(grade, 'insulated_metal')

        unit_cost = self.db.get_cost('spandrel', spandrel_type)
        subtotal = spandrel_area * unit_cost

        items.append(CostBreakdown(
            category='Spandrel',
            item=spandrel_type.replace('_', ' ').title(),
            quantity=spandrel_area,
            unit='m2',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Area de spandrel'
        ))

        return items

    def _calculate_gasket_cost(self, mullions_data, transoms_data, system_type):
        """Calcula costo de empaques."""
        items = []

        # Longitud total de perfiles
        total_length = sum(m.length if hasattr(m, 'length') else 0 for m in mullions_data)
        total_length += sum(t.length if hasattr(t, 'length') else 0 for t in transoms_data)

        # Cada perfil tiene ~4 lineas de empaque
        gasket_length = total_length * 4

        # Tipo de empaque segun sistema
        gasket_type = 'epdm_thermal' if system_type in ['structural_glazing', 'point_fixed'] else 'epdm_standard'
        unit_cost = self.db.get_cost('gaskets', gasket_type)
        subtotal = gasket_length * unit_cost

        items.append(CostBreakdown(
            category='Empaques',
            item=gasket_type.replace('_', ' ').upper(),
            quantity=gasket_length,
            unit='m',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='4 lineas por perfil'
        ))

        return items

    def _calculate_sealant_cost(self, panels_data, system_type):
        """Calcula costo de selladores."""
        items = []

        # Perimetro total de paneles
        panel_count = len(panels_data)
        avg_perimeter = 8  # m promedio por panel (2m x 3.6m aprox)
        total_perimeter = panel_count * avg_perimeter

        # Tipo de sellador
        sealant_type = 'silicone_structural' if system_type == 'structural_glazing' else 'silicone_standard'
        unit_cost = self.db.get_cost('sealants', sealant_type)
        subtotal = total_perimeter * unit_cost

        items.append(CostBreakdown(
            category='Selladores',
            item=sealant_type.replace('_', ' ').title(),
            quantity=total_perimeter,
            unit='m',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Perimetro de paneles'
        ))

        return items

    def _calculate_anchor_cost(self, mullions_data, system_type):
        """Calcula costo de anclajes."""
        items = []

        # Un anclaje cada ~1.8m de mullion
        total_mullion_length = sum(m.length if hasattr(m, 'length') else 0 for m in mullions_data)
        anchor_count = max(1, int(total_mullion_length / 1.8))

        # Tipo de anclaje
        anchor_type = 'seismic' if system_type in ['unitized', 'structural_glazing'] else 'adjustable'
        unit_cost = self.db.get_cost('anchors', anchor_type)
        subtotal = anchor_count * unit_cost

        items.append(CostBreakdown(
            category='Anclajes',
            item=anchor_type.replace('_', ' ').title(),
            quantity=anchor_count,
            unit='pza',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Cada 1.8m de mullion'
        ))

        return items

    def _calculate_hardware_cost(self, mullions_data, transoms_data, system_type):
        """Calcula costo de herrajes."""
        items = []

        mullion_count = len(mullions_data)
        transom_count = len(transoms_data)

        # Clips de transom
        clip_count = transom_count * 2
        unit_cost = self.db.get_cost('hardware', 'transom_clip')
        subtotal = clip_count * unit_cost

        items.append(CostBreakdown(
            category='Herrajes',
            item='Clip de transom',
            quantity=clip_count,
            unit='pza',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='2 por transom'
        ))

        # Brackets de esquina (estimado)
        corner_count = max(4, mullion_count // 5)
        unit_cost = self.db.get_cost('hardware', 'corner_bracket')
        subtotal = corner_count * unit_cost

        items.append(CostBreakdown(
            category='Herrajes',
            item='Bracket de esquina',
            quantity=corner_count,
            unit='pza',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes='Esquinas y juntas'
        ))

        # Placas de presion para structural glazing
        if system_type == 'structural_glazing':
            plate_count = transom_count
            unit_cost = self.db.get_cost('hardware', 'pressure_plate')
            subtotal = plate_count * unit_cost

            items.append(CostBreakdown(
                category='Herrajes',
                item='Placa de presion',
                quantity=plate_count,
                unit='pza',
                unit_cost=unit_cost,
                subtotal=subtotal,
                notes='Structural glazing'
            ))

        return items

    def _calculate_labor_cost(self, panel_summary, system_type, grade):
        """Calcula costo de mano de obra."""
        items = []

        total_area = panel_summary.get('total_area', 0)

        labor_costs = self.db.COSTS['labor'].get(system_type, self.db.COSTS['labor']['stick'])
        unit_cost = labor_costs.get(grade, labor_costs['standard'])
        subtotal = total_area * unit_cost

        items.append(CostBreakdown(
            category='Mano de obra',
            item=f'Instalacion sistema {system_type}',
            quantity=total_area,
            unit='m2',
            unit_cost=unit_cost,
            subtotal=subtotal,
            notes=f'Nivel {grade}'
        ))

        return items

    def generate_report(self, cost_result):
        """
        Genera reporte formateado de costos.

        Args:
            cost_result: CostResult

        Returns:
            str: Reporte formateado
        """
        lines = [
            "=" * 70,
            "REPORTE DE COSTOS - MURO CORTINA PARAMETRICO",
            "=" * 70,
            f"Sistema: {cost_result.system_type.upper()}",
            f"Grado: {cost_result.grade.upper()}",
            f"Area total: {cost_result.total_area:.2f} m2",
            "-" * 70,
            ""
        ]

        # Agrupar por categoria
        categories = {}
        for item in cost_result.breakdown:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        # Imprimir cada categoria
        for category, items in categories.items():
            lines.append(f"{category.upper()}")
            lines.append("-" * 40)

            for item in items:
                qty_str = f"{item.quantity:,.2f}" if isinstance(item.quantity, float) else f"{item.quantity:,}"
                lines.append(
                    f"  {item.item:<25} "
                    f"{qty_str:>10} {item.unit:<4} x "
                    f"${item.unit_cost:>10,.2f} = "
                    f"${item.subtotal:>12,.2f}"
                )

            subtotal = sum(i.subtotal for i in items)
            lines.append(f"  {'Subtotal':<25} {'':>10} {'':>4}   {'':>10}   ${subtotal:>12,.2f}")
            lines.append("")

        # Totales
        lines.append("=" * 70)
        lines.append(f"{'TOTAL':>50} ${cost_result.total_cost:>15,.2f} MXN")
        lines.append(f"{'COSTO POR M2':>50} ${cost_result.cost_per_m2:>15,.2f} MXN/m2")
        lines.append("=" * 70)

        return "\n".join(lines)


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    calculator = CurtainWallCostCalculator()

    result = calculator.calculate(
        mullions_data=profiles_data if 'profiles_data' in dir() else [],
        transoms_data=[],
        panels_data=panel_data if 'panel_data' in dir() else [],
        panel_summary=summary if 'summary' in dir() else {'total_area': 100},
        system_type=system_type if 'system_type' in dir() else 'stick',
        material_grade=material_grade if 'material_grade' in dir() else 'standard'
    )

    # Salidas para Grasshopper
    total_cost = result.total_cost
    cost_breakdown = result.breakdown
    cost_per_m2 = result.cost_per_m2
    report = calculator.generate_report(result)
