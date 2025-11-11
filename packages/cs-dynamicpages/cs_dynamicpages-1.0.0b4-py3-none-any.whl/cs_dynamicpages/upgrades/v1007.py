from . import logger
from cs_dynamicpages.utils import enable_behavior
from plone import api


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Add new behavior")
    enable_behavior("cs_dynamicpages.fetchpriority_image")
    row_types_fields = api.portal.get_registry_record(
        "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields", default=[]
    )
    new_row_types_fields = []

    for row_type_field in row_types_fields:
        if row_type_field["row_type"] in [
            "cs_dynamicpages-slider-view",
            "cs_dynamicpages-features-view",
            "cs_dynamicpages-query-columns-view",
            "cs_dynamicpages-featured-overlay-view",
            "cs_dynamicpages-featured-view",
        ]:
            each_row_type_fields = row_type_field.get("each_row_type_fields", [])
            each_row_type_fields.append("IFetchPriorityImage.fetchpriority_image")
            row_type_field["each_row_type_fields"] = each_row_type_fields
        new_row_types_fields.append(row_type_field)
    api.portal.set_registry_record(
        "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields",
        new_row_types_fields,
    )
