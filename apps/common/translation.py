from modeltranslation.translator import TranslationOptions, register

from apps.common.models import CompanyProfile, Facility, StoryGroup, StoryItem, Tag


@register(CompanyProfile)
class CompanyProfileTranslationOptions(TranslationOptions):
    fields = ("about",)


@register(Facility)
class FacilityTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(StoryGroup)
class StoryGroupTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(StoryItem)
class StoryItemTranslationOptions(TranslationOptions):
    fields = ("description",)


__all__ = [
    "CompanyProfileTranslationOptions",
    "FacilityTranslationOptions",
    "TagTranslationOptions",
    "StoryGroupTranslationOptions",
    "StoryItemTranslationOptions",
]
