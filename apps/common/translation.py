from modeltranslation.translator import register, TranslationOptions

from apps.common.models import CompanyProfile


@register(CompanyProfile)
class CompanyProfileTranslationOptions(TranslationOptions):
    fields = ('about',)
    

__all__ = [
    'CompanyProfileTranslationOptions'
]