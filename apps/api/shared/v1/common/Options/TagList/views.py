from rest_framework.generics import ListAPIView
from apps.common.models import Tag
from apps.api.shared.v1.common.Options.TagList.serializers import TagListSerializer
from rest_framework.permissions import AllowAny


class TagListAPIView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ('id', 'title')
    search_fields = ('title',)
    ordering = ('id', 'title')

__all__ = [
    'TagListAPIView',
]