from plone import api
from plone.app.layout.globals.layout import IBodyClassAdapter
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(IBodyClassAdapter)
class DynamicViewFolderClasses:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_classes(self, template, view):
        """Whenever we are in a dynamic-view, add a custom class
        signaling that the user can edit the content
        """
        if template.id == "dynamic_view.pt":
            can_edit = api.user.has_permission(
                "Modify portal content", obj=self.context
            )
            if can_edit:
                return ["can_edit"]
            return []
        return []
