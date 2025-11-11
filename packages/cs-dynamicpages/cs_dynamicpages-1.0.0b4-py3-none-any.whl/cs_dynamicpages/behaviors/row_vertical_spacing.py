from cs_dynamicpages import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IRowVerticalSpacingMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IRowVerticalSpacing(model.Schema):
    padding_top = schema.Choice(
        title=_("Row padding top"),
        description=_("Select the padding top that this row will have"),
        vocabulary="cs_dynamicpages.RowPaddingTop",
        required=True,
        default="pt-0",
    )
    padding_bottom = schema.Choice(
        title=_("Row padding bottom"),
        description=_("Select the padding bottom that this row will have"),
        vocabulary="cs_dynamicpages.RowPaddingBottom",
        required=True,
        default="pb-0",
    )
    margin_top = schema.Choice(
        title=_("Row margin top"),
        description=_("Select the margin top that this row will have"),
        vocabulary="cs_dynamicpages.RowMarginTop",
        required=True,
        default="mt-0",
    )
    margin_bottom = schema.Choice(
        title=_("Row margin bottom"),
        description=_("Select the margin bottom that this row will have"),
        vocabulary="cs_dynamicpages.RowMarginBottom",
        required=True,
        default="mb-0",
    )


@implementer(IRowVerticalSpacing)
@adapter(IRowVerticalSpacingMarker)
class RowVerticalSpacing:
    def __init__(self, context):
        self.context = context

    @property
    def padding_top(self):
        if safe_hasattr(self.context, "padding_top"):
            return self.context.padding_top
        return None

    @padding_top.setter
    def padding_top(self, value):
        self.context.padding_top = value

    @property
    def padding_bottom(self):
        if safe_hasattr(self.context, "padding_bottom"):
            return self.context.padding_bottom
        return None

    @padding_bottom.setter
    def padding_bottom(self, value):
        self.context.padding_bottom = value

    @property
    def margin_top(self):
        if safe_hasattr(self.context, "margin_top"):
            return self.context.margin_top
        return None

    @margin_top.setter
    def margin_top(self, value):
        self.context.margin_top = value

    @property
    def margin_bottom(self):
        if safe_hasattr(self.context, "margin_bottom"):
            return self.context.margin_bottom
        return None

    @margin_bottom.setter
    def margin_bottom(self, value):
        self.context.margin_bottom = value
