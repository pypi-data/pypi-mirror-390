# from plone import api
from plone import api
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class VocabItem:
    def __init__(self, token, value):
        self.token = token
        self.value = value


@implementer(IVocabularyFactory)
class RowPaddingTop:
    """ """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        values = api.portal.get_registry_record(
            "cs_dynamicpages.dynamic_pages_control_panel.spacer_padding_top",
            default=[],
        )

        terms = []
        for item in values:
            terms.append(
                SimpleTerm(
                    value=item["spacer_class"],
                    token=str(item["spacer_class"]),
                    title=item["spacer_label"],
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


RowPaddingTopFactory = RowPaddingTop()


@implementer(IVocabularyFactory)
class RowPaddingBottom:
    """ """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        values = api.portal.get_registry_record(
            "cs_dynamicpages.dynamic_pages_control_panel.spacer_padding_bottom",
            default=[],
        )

        terms = []
        for item in values:
            terms.append(
                SimpleTerm(
                    value=item["spacer_class"],
                    token=str(item["spacer_class"]),
                    title=item["spacer_label"],
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


RowPaddingBottomFactory = RowPaddingBottom()


@implementer(IVocabularyFactory)
class RowMarginTop:
    """ """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        values = api.portal.get_registry_record(
            "cs_dynamicpages.dynamic_pages_control_panel.spacer_margin_top",
            default=[],
        )

        terms = []
        for item in values:
            terms.append(
                SimpleTerm(
                    value=item["spacer_class"],
                    token=str(item["spacer_class"]),
                    title=item["spacer_label"],
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


RowMarginTopFactory = RowMarginTop()


@implementer(IVocabularyFactory)
class RowMarginBottom:
    """ """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        values = api.portal.get_registry_record(
            "cs_dynamicpages.dynamic_pages_control_panel.spacer_margin_bottom",
            default=[],
        )

        terms = []
        for item in values:
            terms.append(
                SimpleTerm(
                    value=item["spacer_class"],
                    token=str(item["spacer_class"]),
                    title=item["spacer_label"],
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


RowMarginBottomFactory = RowMarginBottom()
