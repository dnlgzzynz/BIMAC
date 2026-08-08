"""
Cost Calculator

Calculadora de costos para cubiertas paramétricas.
Soporta múltiples materiales, descuentos por volumen y factores adicionales.
"""

from collections import namedtuple
import os

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Estructura de resultado
CostBreakdown = namedtuple('CostBreakdown', [
    'panel_type',
    'material',
    'quantity',
    'area',
    'cost_per_m2',
    'subtotal'
])

ProjectCost = namedtuple('ProjectCost', [
    'panels_cost',
    'structure_cost',
    'installation_cost',
    'contingency',
    'total',
    'budget',
    'margin',
    'margin_percent',
    'is_within_budget'
])


class CostCalculator:
    """
    Calculadora de costos para cubiertas.

    Calcula costos basados en:
    - Tipo de panel (flat, single_curve, double_curve)
    - Material seleccionado
    - Factores adicionales (estructura, instalación, contingencia)
    - Descuentos por volumen

    Example:
        >>> calculator = CostCalculator(material="polycarbonate_16mm")
        >>> result = calculator.calculate(
        ...     flat_panels=flat_list,
        ...     single_curve=single_list,
        ...     double_curve=double_list,
        ...     budget=280000
        ... )
        >>> print(result.total)
    """

    # Costos por defecto (MXN/m²)
    DEFAULT_COSTS = {
        "polycarbonate_16mm": {
            "flat": 450,
            "single_curve": 680,
            "double_curve": 1250,
        },
        "polycarbonate_10mm": {
            "flat": 380,
            "single_curve": 580,
            "double_curve": 1100,
        },
        "glass_laminated": {
            "flat": 1200,
            "single_curve": 1800,
            "double_curve": 2500,
        },
        "etfe_single": {
            "flat": 800,
            "single_curve": 1100,
            "double_curve": 1500,
        },
        "metal_composite": {
            "flat": 350,
            "single_curve": 550,
            "double_curve": 950,
        },
    }

    # Factores adicionales
    DEFAULT_FACTORS = {
        "structure": 0.25,      # 25% del costo de paneles
        "installation": 0.15,   # 15% del subtotal
        "contingency": 0.10,    # 10% de imprevistos
    }

    # Descuentos por volumen
    DEFAULT_DISCOUNTS = [
        {"min_area": 500, "discount": 0.05},
        {"min_area": 1000, "discount": 0.10},
        {"min_area": 2000, "discount": 0.15},
    ]

    def __init__(self, material="polycarbonate_16mm", costs=None, factors=None,
                 discounts=None, config_path=None):
        """
        Inicializa la calculadora.

        Args:
            material: Tipo de material para paneles
            costs: Diccionario de costos personalizados
            factors: Factores adicionales personalizados
            discounts: Descuentos por volumen personalizados
            config_path: Ruta a archivo de configuración YAML
        """
        self.material = material

        # Cargar configuración desde archivo si existe
        if config_path and YAML_AVAILABLE:
            self._load_config(config_path)
        else:
            self.costs = costs or self.DEFAULT_COSTS.copy()
            self.factors = factors or self.DEFAULT_FACTORS.copy()
            self.discounts = discounts or self.DEFAULT_DISCOUNTS.copy()

    def _load_config(self, config_path):
        """Carga configuración desde archivo YAML."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.costs = config.get('panels', self.DEFAULT_COSTS)
                self.factors = config.get('factors', self.DEFAULT_FACTORS)
                self.discounts = config.get('volume_discounts', self.DEFAULT_DISCOUNTS)
        except Exception:
            self.costs = self.DEFAULT_COSTS.copy()
            self.factors = self.DEFAULT_FACTORS.copy()
            self.discounts = self.DEFAULT_DISCOUNTS.copy()

    def calculate(self, flat_panels=None, single_curve=None, double_curve=None,
                  flat_area=None, single_area=None, double_area=None,
                  budget=None):
        """
        Calcula el costo total del proyecto.

        Puede recibir listas de paneles (Breps) o áreas directamente.

        Args:
            flat_panels: Lista de paneles planos
            single_curve: Lista de paneles curvatura simple
            double_curve: Lista de paneles doble curvatura
            flat_area: Área de paneles planos (m²) - alternativa
            single_area: Área de paneles curvatura simple (m²)
            double_area: Área de paneles doble curvatura (m²)
            budget: Presupuesto disponible

        Returns:
            tuple: (ProjectCost, dict de breakdowns)
        """
        # Calcular áreas si se proporcionan paneles
        if flat_panels is not None:
            flat_area = self._calculate_area(flat_panels)
            flat_qty = len(flat_panels)
        else:
            flat_area = flat_area or 0
            flat_qty = int(flat_area / 3)  # Estimación

        if single_curve is not None:
            single_area = self._calculate_area(single_curve)
            single_qty = len(single_curve)
        else:
            single_area = single_area or 0
            single_qty = int(single_area / 3)

        if double_curve is not None:
            double_area = self._calculate_area(double_curve)
            double_qty = len(double_curve)
        else:
            double_area = double_area or 0
            double_qty = int(double_area / 3)

        # Obtener costos del material
        material_costs = self.costs.get(self.material, self.costs.get("polycarbonate_16mm"))

        # Calcular costos por tipo
        flat_breakdown = CostBreakdown(
            panel_type="flat",
            material=self.material,
            quantity=flat_qty,
            area=flat_area,
            cost_per_m2=material_costs["flat"],
            subtotal=flat_area * material_costs["flat"]
        )

        single_breakdown = CostBreakdown(
            panel_type="single_curve",
            material=self.material,
            quantity=single_qty,
            area=single_area,
            cost_per_m2=material_costs["single_curve"],
            subtotal=single_area * material_costs["single_curve"]
        )

        double_breakdown = CostBreakdown(
            panel_type="double_curve",
            material=self.material,
            quantity=double_qty,
            area=double_area,
            cost_per_m2=material_costs["double_curve"],
            subtotal=double_area * material_costs["double_curve"]
        )

        breakdowns = {
            "flat": flat_breakdown,
            "single_curve": single_breakdown,
            "double_curve": double_breakdown,
        }

        # Costo total de paneles
        panels_cost = (
            flat_breakdown.subtotal +
            single_breakdown.subtotal +
            double_breakdown.subtotal
        )

        # Aplicar descuento por volumen
        total_area = flat_area + single_area + double_area
        discount = self._get_volume_discount(total_area)
        panels_cost *= (1 - discount)

        # Costos adicionales
        structure_cost = panels_cost * self.factors.get("structure", 0.25)
        subtotal = panels_cost + structure_cost

        installation_cost = subtotal * self.factors.get("installation", 0.15)
        subtotal += installation_cost

        contingency = subtotal * self.factors.get("contingency", 0.10)

        total = subtotal + contingency

        # Comparar con presupuesto
        budget = budget or 0
        margin = budget - total if budget > 0 else 0
        margin_percent = (margin / budget * 100) if budget > 0 else 0
        is_within_budget = total <= budget if budget > 0 else True

        project_cost = ProjectCost(
            panels_cost=panels_cost,
            structure_cost=structure_cost,
            installation_cost=installation_cost,
            contingency=contingency,
            total=total,
            budget=budget,
            margin=margin,
            margin_percent=margin_percent,
            is_within_budget=is_within_budget
        )

        return project_cost, breakdowns

    def _calculate_area(self, panels):
        """
        Calcula el área total de una lista de paneles.

        Args:
            panels: Lista de Breps

        Returns:
            float: Área en m²
        """
        if panels is None:
            return 0

        try:
            import Rhino.Geometry as rg

            total = 0
            for panel in panels:
                if panel is None:
                    continue
                props = rg.AreaMassProperties.Compute(panel)
                if props:
                    total += props.Area / 1000000  # mm² a m²

            return total
        except ImportError:
            # Si no hay Rhino, asumir área basada en cantidad
            return len(panels) * 3.0  # 3 m² promedio

    def _get_volume_discount(self, total_area):
        """
        Obtiene el descuento por volumen.

        Args:
            total_area: Área total en m²

        Returns:
            float: Factor de descuento (0-1)
        """
        discount = 0

        for tier in sorted(self.discounts, key=lambda x: x["min_area"], reverse=True):
            if total_area >= tier["min_area"]:
                discount = tier["discount"]
                break

        return discount

    def generate_report(self, project_cost, breakdowns):
        """
        Genera un reporte de costos formateado.

        Args:
            project_cost: ProjectCost
            breakdowns: Dict de CostBreakdown

        Returns:
            str: Reporte formateado
        """
        flat = breakdowns["flat"]
        single = breakdowns["single_curve"]
        double = breakdowns["double_curve"]

        total_qty = flat.quantity + single.quantity + double.quantity
        total_area = flat.area + single.area + double.area

        status = "DENTRO DE PRESUPUESTO" if project_cost.is_within_budget else "EXCEDE PRESUPUESTO"

        report = f"""
================================================================================
                    ANÁLISIS DE COSTOS - CUBIERTA PARAMÉTRICA
================================================================================

MATERIAL: {self.material}

DESGLOSE POR TIPO DE PANEL:
--------------------------------------------------------------------------------
  Tipo                 | Cantidad |  Área (m²) |   Costo/m²  |      Subtotal
--------------------------------------------------------------------------------
  Paneles Planos       |   {flat.quantity:5d}  |  {flat.area:8.2f}  |  ${flat.cost_per_m2:>8,.0f}  |  ${flat.subtotal:>12,.2f}
  Curvatura Simple     |   {single.quantity:5d}  |  {single.area:8.2f}  |  ${single.cost_per_m2:>8,.0f}  |  ${single.subtotal:>12,.2f}
  Doble Curvatura      |   {double.quantity:5d}  |  {double.area:8.2f}  |  ${double.cost_per_m2:>8,.0f}  |  ${double.subtotal:>12,.2f}
--------------------------------------------------------------------------------
  SUBTOTAL PANELES     |   {total_qty:5d}  |  {total_area:8.2f}  |            |  ${project_cost.panels_cost:>12,.2f}
--------------------------------------------------------------------------------

COSTOS ADICIONALES:
--------------------------------------------------------------------------------
  Estructura metálica ({self.factors.get('structure', 0.25)*100:.0f}%)                    |  ${project_cost.structure_cost:>12,.2f}
  Instalación ({self.factors.get('installation', 0.15)*100:.0f}%)                         |  ${project_cost.installation_cost:>12,.2f}
  Contingencia ({self.factors.get('contingency', 0.10)*100:.0f}%)                         |  ${project_cost.contingency:>12,.2f}
--------------------------------------------------------------------------------

================================================================================
  COSTO TOTAL PROYECTO                               |  ${project_cost.total:>12,.2f} MXN
================================================================================
  Presupuesto disponible                             |  ${project_cost.budget:>12,.2f} MXN
  Margen                                             |  ${project_cost.margin:>12,.2f} MXN
  Porcentaje de margen                               |  {project_cost.margin_percent:>11.1f}%
================================================================================

  ESTADO: [{status}]

================================================================================
"""
        return report

    def get_available_materials(self):
        """Retorna lista de materiales disponibles."""
        return list(self.costs.keys())

    def get_material_costs(self, material=None):
        """Retorna costos de un material."""
        material = material or self.material
        return self.costs.get(material, {})


# Función de conveniencia
def calculate_costs(flat_panels=None, single_curve=None, double_curve=None,
                    flat_area=None, single_area=None, double_area=None,
                    material="polycarbonate_16mm", budget=None):
    """
    Calcula costos de un proyecto de cubierta.

    Args:
        flat_panels: Lista de paneles planos (o flat_area)
        single_curve: Lista de paneles curvatura simple (o single_area)
        double_curve: Lista de paneles doble curvatura (o double_area)
        material: Tipo de material
        budget: Presupuesto disponible

    Returns:
        tuple: (ProjectCost, breakdowns)
    """
    calculator = CostCalculator(material=material)
    return calculator.calculate(
        flat_panels=flat_panels,
        single_curve=single_curve,
        double_curve=double_curve,
        flat_area=flat_area,
        single_area=single_area,
        double_area=double_area,
        budget=budget
    )
