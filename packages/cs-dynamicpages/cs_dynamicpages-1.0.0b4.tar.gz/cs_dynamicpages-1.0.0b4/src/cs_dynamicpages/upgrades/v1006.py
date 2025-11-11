from . import logger
from cs_dynamicpages.utils import enable_behavior
from plone import api


def upgrade(setup_tool=None):
    """ """
    logger.info(
        "Running upgrade (Python): Add new values on row_type_fields in registry"
    )
    enable_behavior("cs_dynamicpages.row_vertical_spacing")
    row_types_fields = api.portal.get_registry_record(
        "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields", default=[]
    )
    new_row_types_fields = []

    for row_type_field in row_types_fields:
        each_row_type_fields = row_type_field.get("each_row_type_fields", [])
        each_row_type_fields.append("IRowVerticalSpacing.padding_top")
        each_row_type_fields.append("IRowVerticalSpacing.padding_bottom")
        each_row_type_fields.append("IRowVerticalSpacing.margin_top")
        each_row_type_fields.append("IRowVerticalSpacing.margin_bottom")
        row_type_field["each_row_type_fields"] = each_row_type_fields
        new_row_types_fields.append(row_type_field)
    api.portal.set_registry_record(
        "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields",
        new_row_types_fields,
    )
