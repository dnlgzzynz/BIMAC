"""
update_schedule.py
Script PyRevit para actualizar schedules de la cubierta del museo.

Proyecto: Cubierta Orgánica de Museo
Autor: BIMAC
Versión: 1.0.0

Uso en PyRevit:
    1. Copiar este archivo a la extensión PyRevit
    2. Ejecutar desde el ribbon de PyRevit
    3. Selecciona el schedule a actualizar o crea uno nuevo

Funcionalidades:
    - Crear schedule de paneles de cubierta
    - Actualizar totales de costos
    - Exportar a Excel
    - Sincronizar con n8n webhook
"""

# -*- coding: utf-8 -*-
from __future__ import print_function

# =============================================================================
# IMPORTS
# =============================================================================

# PyRevit
from pyrevit import revit, DB, forms, script

# Standard library
import os
import json
from datetime import datetime

# Para HTTP requests (si disponible)
try:
    import urllib2
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Nombre del schedule
SCHEDULE_NAME = "BIMAC_Cubierta_Paneles"
SCHEDULE_SUMMARY_NAME = "BIMAC_Cubierta_Resumen"

# Categoría de elementos
TARGET_CATEGORY = DB.BuiltInCategory.OST_GenericModel

# Parámetros BIMAC
BIMAC_PARAMS = {
    "type": "BIMAC_PanelType",
    "cost": "BIMAC_TotalCost",
    "cost_m2": "BIMAC_CostPerM2",
    "material": "BIMAC_Material",
    "panel_id": "BIMAC_PanelID",
    "area": "BIMAC_Area"
}

# Webhook URL (configurar en variables de entorno)
WEBHOOK_URL = os.environ.get(
    "BIMAC_WEBHOOK_URL",
    "http://localhost:5678/webhook/cubierta-cost-update"
)

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_logger():
    """Obtiene el logger de PyRevit."""
    return script.get_logger()


def get_all_panels(doc):
    """
    Obtiene todos los paneles de cubierta del modelo.

    Args:
        doc (Document): Documento de Revit

    Returns:
        list: Lista de elementos (paneles)
    """
    collector = DB.FilteredElementCollector(doc)\
        .OfCategory(TARGET_CATEGORY)\
        .WhereElementIsNotElementType()

    panels = []

    for element in collector:
        # Verificar que tenga parámetro BIMAC
        param = element.LookupParameter(BIMAC_PARAMS["panel_id"])
        if param is not None and param.HasValue:
            panels.append(element)

    return panels


def get_param_value(element, param_name, default=None):
    """
    Obtiene el valor de un parámetro de un elemento.

    Args:
        element: Elemento de Revit
        param_name (str): Nombre del parámetro
        default: Valor por defecto si no existe

    Returns:
        Valor del parámetro o default
    """
    param = element.LookupParameter(param_name)

    if param is None:
        return default

    if not param.HasValue:
        return default

    storage_type = param.StorageType

    if storage_type == DB.StorageType.String:
        return param.AsString()
    elif storage_type == DB.StorageType.Double:
        return param.AsDouble()
    elif storage_type == DB.StorageType.Integer:
        return param.AsInteger()
    elif storage_type == DB.StorageType.ElementId:
        return param.AsElementId().IntegerValue

    return default


def calculate_totals(panels):
    """
    Calcula totales de costos y cantidades.

    Args:
        panels (list): Lista de paneles

    Returns:
        dict: Diccionario con totales
    """
    totals = {
        "flat": {"count": 0, "area": 0, "cost": 0},
        "single_curve": {"count": 0, "area": 0, "cost": 0},
        "double_curve": {"count": 0, "area": 0, "cost": 0},
        "total": {"count": 0, "area": 0, "cost": 0}
    }

    for panel in panels:
        panel_type = get_param_value(panel, BIMAC_PARAMS["type"], "flat")
        cost = get_param_value(panel, BIMAC_PARAMS["cost"], 0)
        area = get_param_value(panel, BIMAC_PARAMS["area"], 0)

        if panel_type in totals:
            totals[panel_type]["count"] += 1
            totals[panel_type]["area"] += area
            totals[panel_type]["cost"] += cost

        totals["total"]["count"] += 1
        totals["total"]["area"] += area
        totals["total"]["cost"] += cost

    return totals


def format_currency(amount):
    """Formatea un número como moneda MXN."""
    return "${:,.2f}".format(amount)


# =============================================================================
# FUNCIONES DE SCHEDULE
# =============================================================================

def find_schedule(doc, name):
    """
    Busca un schedule por nombre.

    Args:
        doc (Document): Documento de Revit
        name (str): Nombre del schedule

    Returns:
        ViewSchedule o None
    """
    collector = DB.FilteredElementCollector(doc)\
        .OfClass(DB.ViewSchedule)

    for schedule in collector:
        if schedule.Name == name:
            return schedule

    return None


def create_panel_schedule(doc):
    """
    Crea un nuevo schedule de paneles.

    Args:
        doc (Document): Documento de Revit

    Returns:
        ViewSchedule
    """
    # Obtener ID de categoría
    category_id = DB.ElementId(TARGET_CATEGORY)

    # Crear schedule
    schedule = DB.ViewSchedule.CreateSchedule(doc, category_id)
    schedule.Name = SCHEDULE_NAME

    # Obtener definición del schedule
    definition = schedule.Definition

    # Agregar campos
    # 1. Panel ID
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["panel_id"])

    # 2. Panel Type
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["type"])

    # 3. Area
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["area"])

    # 4. Cost per m²
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["cost_m2"])

    # 5. Total Cost
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["cost"])

    # 6. Material
    add_field_to_schedule(doc, definition, BIMAC_PARAMS["material"])

    return schedule


def add_field_to_schedule(doc, definition, param_name):
    """
    Agrega un campo al schedule.

    Args:
        doc (Document): Documento
        definition: Definición del schedule
        param_name (str): Nombre del parámetro
    """
    try:
        # Buscar el parámetro en los schedulable fields
        schedulable_fields = definition.GetSchedulableFields()

        for field_id in schedulable_fields:
            field = definition.GetField(field_id)
            if field is not None:
                if field.GetName() == param_name:
                    definition.AddField(field_id)
                    return True

    except Exception as ex:
        get_logger().warning(
            "No se pudo agregar campo {}: {}".format(param_name, ex)
        )

    return False


def update_schedule_totals(doc, schedule, totals):
    """
    Actualiza los totales en el schedule.

    Args:
        doc (Document): Documento
        schedule (ViewSchedule): Schedule a actualizar
        totals (dict): Diccionario de totales
    """
    # Los schedules de Revit calculan automáticamente los totales
    # si están configurados correctamente.
    # Esta función es un placeholder para lógica adicional.
    pass


# =============================================================================
# FUNCIONES DE EXPORTACIÓN
# =============================================================================

def export_to_excel(doc, schedule, output_path):
    """
    Exporta el schedule a Excel.

    Args:
        doc (Document): Documento
        schedule (ViewSchedule): Schedule a exportar
        output_path (str): Ruta de salida

    Returns:
        bool: True si exitoso
    """
    try:
        # Configurar opciones de exportación
        options = DB.ViewScheduleExportOptions()
        options.FieldDelimiter = ","
        options.Title = False
        options.HeadersFootersBlanks = False

        # Exportar como CSV temporal
        csv_path = output_path.replace(".xlsx", ".csv")
        schedule.Export(os.path.dirname(csv_path),
                       os.path.basename(csv_path),
                       options)

        get_logger().info("Schedule exportado a: {}".format(csv_path))
        return True

    except Exception as ex:
        get_logger().error("Error exportando: {}".format(ex))
        return False


def send_to_webhook(totals):
    """
    Envía los totales al webhook de n8n.

    Args:
        totals (dict): Diccionario de totales

    Returns:
        bool: True si exitoso
    """
    if not HTTP_AVAILABLE:
        get_logger().warning("HTTP no disponible, no se puede enviar a webhook")
        return False

    try:
        # Preparar datos
        data = {
            "project": "Cubierta Museo Organica",
            "timestamp": datetime.now().isoformat(),
            "panels": {
                "flat": {
                    "quantity": totals["flat"]["count"],
                    "area_m2": round(totals["flat"]["area"], 2),
                    "cost": round(totals["flat"]["cost"], 2)
                },
                "single_curve": {
                    "quantity": totals["single_curve"]["count"],
                    "area_m2": round(totals["single_curve"]["area"], 2),
                    "cost": round(totals["single_curve"]["cost"], 2)
                },
                "double_curve": {
                    "quantity": totals["double_curve"]["count"],
                    "area_m2": round(totals["double_curve"]["area"], 2),
                    "cost": round(totals["double_curve"]["cost"], 2)
                }
            },
            "total_cost": round(totals["total"]["cost"], 2),
            "total_panels": totals["total"]["count"],
            "total_area": round(totals["total"]["area"], 2)
        }

        # Enviar request
        json_data = json.dumps(data)
        request = urllib2.Request(
            WEBHOOK_URL,
            json_data,
            {'Content-Type': 'application/json'}
        )
        response = urllib2.urlopen(request)

        if response.getcode() == 200:
            get_logger().info("Datos enviados a webhook exitosamente")
            return True

    except Exception as ex:
        get_logger().error("Error enviando a webhook: {}".format(ex))

    return False


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal del script."""
    doc = revit.doc
    logger = get_logger()

    logger.info("=" * 60)
    logger.info("BIMAC - Actualización de Schedule de Cubierta")
    logger.info("=" * 60)

    # Obtener paneles
    panels = get_all_panels(doc)

    if not panels:
        forms.alert(
            "No se encontraron paneles con parámetros BIMAC.\n"
            "Asegúrese de haber exportado desde Grasshopper.",
            title="Sin paneles"
        )
        return

    logger.info("Paneles encontrados: {}".format(len(panels)))

    # Calcular totales
    totals = calculate_totals(panels)

    # Mostrar resumen
    message = """
RESUMEN DE PANELES DE CUBIERTA

Paneles Planos:        {} uds  |  {} m²  |  {}
Curvatura Simple:      {} uds  |  {} m²  |  {}
Doble Curvatura:       {} uds  |  {} m²  |  {}
---------------------------------------------
TOTAL:                 {} uds  |  {} m²  |  {}

¿Desea actualizar el schedule?
""".format(
        totals["flat"]["count"],
        round(totals["flat"]["area"], 1),
        format_currency(totals["flat"]["cost"]),

        totals["single_curve"]["count"],
        round(totals["single_curve"]["area"], 1),
        format_currency(totals["single_curve"]["cost"]),

        totals["double_curve"]["count"],
        round(totals["double_curve"]["area"], 1),
        format_currency(totals["double_curve"]["cost"]),

        totals["total"]["count"],
        round(totals["total"]["area"], 1),
        format_currency(totals["total"]["cost"])
    )

    if not forms.alert(message, yes=True, no=True, title="Actualizar Schedule"):
        return

    # Buscar o crear schedule
    with revit.Transaction("BIMAC - Actualizar Schedule"):
        schedule = find_schedule(doc, SCHEDULE_NAME)

        if schedule is None:
            logger.info("Creando nuevo schedule...")
            schedule = create_panel_schedule(doc)
        else:
            logger.info("Schedule existente encontrado")

        # Actualizar totales
        update_schedule_totals(doc, schedule, totals)

    # Preguntar si enviar a webhook
    if forms.alert(
        "¿Desea enviar los datos al webhook de n8n?",
        yes=True, no=True,
        title="Sincronizar con n8n"
    ):
        success = send_to_webhook(totals)
        if success:
            forms.alert("Datos enviados exitosamente", title="Webhook")

    # Preguntar si exportar
    if forms.alert(
        "¿Desea exportar el schedule a CSV?",
        yes=True, no=True,
        title="Exportar"
    ):
        export_path = forms.save_file(
            file_ext="csv",
            default_name="{}_export.csv".format(SCHEDULE_NAME)
        )
        if export_path:
            export_to_excel(doc, schedule, export_path)
            forms.alert(
                "Exportado a:\n{}".format(export_path),
                title="Exportación completada"
            )

    logger.info("Proceso completado")
    forms.alert(
        "Schedule actualizado exitosamente.\n\n"
        "Total de paneles: {}\n"
        "Costo total: {}".format(
            totals["total"]["count"],
            format_currency(totals["total"]["cost"])
        ),
        title="Completado"
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
