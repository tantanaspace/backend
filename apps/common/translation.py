from modeltranslation.translator import register, TranslationOptions

from apps.common.models import CompanyProfile, Facility, Tag, StoryGroup, StoryItem


@register(CompanyProfile)
class CompanyProfileTranslationOptions(TranslationOptions):
    fields = ('about',)
    

@register(Facility)
class FacilityTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(StoryGroup)
class StoryGroupTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(StoryItem)
class StoryItemTranslationOptions(TranslationOptions):
    fields = ('description',)


__all__ = [
    'CompanyProfileTranslationOptions',
    'FacilityTranslationOptions',
    'TagTranslationOptions',
    'StoryGroupTranslationOptions',
    'StoryItemTranslationOptions',
]