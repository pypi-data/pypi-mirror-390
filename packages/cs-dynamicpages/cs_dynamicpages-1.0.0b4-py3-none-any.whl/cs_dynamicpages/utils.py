from cs_dynamicpages import logger
from plone import api
from plone.app.uuid.utils import uuidToObject
from urllib.parse import urlparse
from zope.component import getSiteManager
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.interface import providedBy


VIEW_PREFIX = "cs_dynamicpages-"

# links starting with these URL scheme should not be redirected to
NON_REDIRECTABLE_URL_SCHEMES = [
    "mailto:",
    "tel:",
    "callto:",  # nonstandard according to RFC 3966. used for skype.
    "webdav:",
    "caldav:",
]

# links starting with these URL scheme should not be resolved to paths
NON_RESOLVABLE_URL_SCHEMES = [*NON_REDIRECTABLE_URL_SCHEMES, "file:", "ftp:"]


def add_custom_view(
    view_name: str,
    shown_fields: list[str],
    has_button: bool = False,
    icon: str = "bricks",
):
    """utility function to add a given view to the list of available row types"""
    record_name = "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields"
    values = api.portal.get_registry_record(record_name)
    new_item = {
        "row_type": view_name,
        "each_row_type_fields": shown_fields,
        "row_type_has_featured_add_button": has_button,
        "row_type_icon": icon,
    }
    values.append(new_item)
    api.portal.set_registry_record(record_name, values)
    logger.info("Added new row type: %s", view_name)

    return True


def enable_behavior(behavior_dotted_name=str):
    """
    utility function to enable the given behavior in the DynamicPageRow content type
    """
    # Get the portal_types tool, which manages all content type definitions (FTIs)
    portal_types = api.portal.get_tool("portal_types")

    # Get the Factory Type Information (FTI) for our specific content type
    fti = getattr(portal_types, "DynamicPageRow", None)

    if not fti:
        # Failsafe in case the content type doesn't exist
        print("Content type 'DynamicPageRow' not found.")
        return

    # Get the current list of behaviors
    behaviors = list(fti.behaviors)

    # --- The Core Logic ---
    # Check if the behavior is already enabled to avoid duplicates
    if behavior_dotted_name not in behaviors:
        print(f"Enabling behavior '{behavior_dotted_name}' on 'DynamicPageRow'.")
        # Add the new behavior to the list
        behaviors.append(behavior_dotted_name)
        # Assign the updated list back to the FTI's behaviors attribute
        fti.behaviors = tuple(behaviors)
    else:
        print(
            f"Behavior '{behavior_dotted_name}' is already enabled on 'DynamicPageRow'."
        )


def get_available_views_for_row():
    from cs_dynamicpages.content.dynamic_page_row import IDynamicPageRow

    items = []
    sm = getSiteManager()

    available_views = sm.adapters.lookupAll(
        required=(IDynamicPageRow, providedBy(getRequest())),
        provided=Interface,
    )

    values = api.portal.get_registry_record(
        "cs_dynamicpages.dynamic_pages_control_panel.row_type_fields", default=[]
    )

    for item in available_views:
        if item[0].startswith(VIEW_PREFIX):
            for value in values:
                item_dict = {
                    "row_type": item[0],
                    "each_row_type_fields": [],
                    "row_type_has_featured_add_button": False,
                    "row_type_icon": "bricks",
                }
                if item[0] == value["row_type"] and value not in items:
                    item_dict = value
                    items.append(item_dict)
    return items


def normalize_uid_from_path(url=None):
    """
    Args:
        url (string): a path or orl

    Returns:
        tuple: tuple of (uid, fragment) a fragment is an anchor id e.g. #head1
    """
    uid = None
    fragment = None

    if not url:
        return uid, fragment

    # resolve uid
    paths = url.split("/")
    paths_lower = [_item.lower() for _item in paths]

    if "resolveuid" in paths_lower:
        ri = paths_lower.index("resolveuid")
        if ri + 1 != len(paths):
            uid = paths[ri + 1]
            if uid == "":
                uid = None

    if not uid:
        return uid, fragment

    # resolve fragment
    parts = urlparse(uid)

    uid = parts.path

    fragment = f"#{parts.fragment}" if parts.fragment else None

    return uid, fragment


def _url_uses_scheme(schemes, url):
    return any(url.startswith(scheme) for scheme in schemes)


def absolute_target_url(url):
    """Compute the absolute target URL."""

    if _url_uses_scheme(NON_RESOLVABLE_URL_SCHEMES, url):
        # For non http/https url schemes, there is no path to resolve.
        return url

    else:
        if "resolveuid" in url:
            uid, fragment = normalize_uid_from_path(url)
            obj = uuidToObject(uid)
            if obj is None:
                # uid can't resolve, return the url
                return url

            url = obj.absolute_url()
            if fragment is not None:
                url = f"{url}{fragment}"
    return url
