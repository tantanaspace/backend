from modeltranslation.translator import TranslationOptions, register

from apps.venues.models import Company, VenueCategory, Venue, VenueZone


@register(Company)
class CompanyTranslationOption(TranslationOptions):
    fields = ('name',)

@register(VenueCategory)
class VenueCategoryTranslationOption(TranslationOptions):
    fields = ('title',)


@register(Venue)
class VenueTranslationOption(TranslationOptions):
    fields = ('name', 'description', 'location')


@register(VenueZone)
class VenueZoneTranslationOption(TranslationOptions):
    fields = ('name',)
    

__all__ = [
    'CompanyTranslationOption',
    'VenueCategoryTranslationOption',
    'VenueTranslationOption',
    'VenueZoneTranslationOption',
]