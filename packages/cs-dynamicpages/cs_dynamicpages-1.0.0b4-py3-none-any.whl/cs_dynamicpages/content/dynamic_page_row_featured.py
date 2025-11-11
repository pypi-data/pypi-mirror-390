# from plone.app.textfield import RichText
# from plone.autoform import directives
from cs_dynamicpages.utils import absolute_target_url
from plone import api
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.dexterity.content import Item

# from plone.namedfile import field as namedfile
from plone.supermodel import model

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer


# from cs_dynamicpages import _


class IDynamicPageRowFeatured(model.Schema):
    """Marker interface and Dexterity Python Schema for DynamicPageRowFeatured"""


@implementer(IDynamicPageRowFeatured)
class DynamicPageRowFeatured(Item):
    """Content-type class for IDynamicPageRowFeatured"""

    def review_state(self):
        return api.content.get_state(obj=self)

    def related_image_object(self):
        related_image = self.related_image
        if related_image:
            return related_image[0].to_object
        return None

    def url(self):
        """Returns the url with link variables replaced."""
        url = replace_link_variables_by_paths(self, self.link_url.strip())
        return absolute_target_url(url)
