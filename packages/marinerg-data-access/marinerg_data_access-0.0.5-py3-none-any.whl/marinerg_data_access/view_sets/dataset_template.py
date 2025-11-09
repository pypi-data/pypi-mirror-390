from rest_framework import permissions

from ichec_django_core.models import Member
from ichec_django_core.view_sets import (
    SearchableModelViewSet,
    OwnerFullOrDjangoModelPermissions,
)

from marinerg_data_access.models import DatasetTemplate
from marinerg_data_access.serializers import DatasetTemplateSerializer


class DatasetTemplatePermissions(OwnerFullOrDjangoModelPermissions):
    owner_field = "creator"


class DatasetTemplateViewSet(SearchableModelViewSet):
    queryset = DatasetTemplate.objects.all()
    serializer_class = DatasetTemplateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        DatasetTemplatePermissions,
    ]

    ordering_fields = SearchableModelViewSet.ordering_fields
    ordering: tuple[str, ...] = ("created_at",)
    search_fields = ["title"]

    def perform_create(self, serializer):
        serializer.save(creator=Member.objects.get(id=self.request.user.id))
