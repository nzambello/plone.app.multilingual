# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import (
    ITranslationFactory,
    ILanguageIndependentFieldsManager,
    ITranslationLocator,
    ITranslationCloner,
    ITranslationIdChooser,
    ITranslationManager,
)
from zope import interface
from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class DefaultLanguageIndependentFieldsManager(object):
    """ Default language independent fields manager.
    """
    interface.implements(ILanguageIndependentFieldsManager)

    def __init__(self, context):
        self.context = context

    def get_field_names(self):
        return []

    def copy_fields(self, translation):
        return


class DefaultTranslationLocator(object):

    interface.implements(ITranslationLocator)

    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        """
        Look for the closest translated folder or siteroot
        """
        parent = aq_parent(self.context)
        translated_parent = parent
        found = False
        while not IPloneSiteRoot.providedBy(parent) and not found:
            parent_translation = ITranslationManager(parent)
            if parent_translation.has_translation(language):
                translated_parent = parent_translation.get_translation(language)
                found = True
            parent = aq_parent(parent)
        return translated_parent


class DefaultTranslationCloner(object):

    interface.implements(ITranslationCloner)

    def __init__(self, context):
        self.context = context

    def __call__(self, object):
        return


class DefaultTranslationIdChooser(object):

    interface.implements(ITranslationIdChooser)

    def __init__(self, context):
        self.context = context

    def __call__(self, parent, language):
        content_id = self.context.getId()
        splitted = content_id.split('-')
        # ugly heuristic (searching for something like 'de', 'en' etc.)
        if len(splitted) > 1 and len(splitted[-1]) == 2:
            content_id = ''.join(splitted[:-1])
        while content_id in parent.objectIds():
            content_id = "%s-%s" % (content_id, language)
        return content_id


class DefaultTranslationFactory(object):

    interface.implements(ITranslationFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        content_type = self.context.portal_type
        # parent for translation
        locator = ITranslationLocator(self.context)
        parent = locator(language)
        # id for translation
        name_chooser = ITranslationIdChooser(self.context)
        content_id = name_chooser(parent, language)
        # creating the translation
        new_id = parent.invokeFactory(
            type_name=content_type,
            id=content_id,
            language=language)
        new_content = getattr(parent, new_id)
        # clone language-independent content
        cloner = ITranslationCloner(self.context)
        cloner(new_content)
        return new_content
