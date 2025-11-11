from cs_dynamicpages import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IFetchPriorityImageMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IFetchPriorityImage(model.Schema):
    """ """

    fetchpriority_image = schema.Bool(
        title=_("Fetch priority image"),
        description=_(
            "Set this to true if you want to signal that this image has a 'high' fetch "
            "priority, otherwise 'auto' will be used. When using 'high' the value of "
            "the loading attribute will be set to 'eager', and 'lazy' when "
            "it is not set."
        ),
        required=False,
    )


@implementer(IFetchPriorityImage)
@adapter(IFetchPriorityImageMarker)
class FetchPriorityImage:
    def __init__(self, context):
        self.context = context

    @property
    def fetchpriority_image(self):
        if safe_hasattr(self.context, "fetchpriority_image"):
            return self.context.fetchpriority_image
        return None

    @fetchpriority_image.setter
    def fetchpriority_image(self, value):
        self.context.fetchpriority_image = value
