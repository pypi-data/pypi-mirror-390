from rest_framework import permissions

from ichec_django_core.models import Member
from ichec_django_core.view_sets import (
    SearchableModelViewSet,
    OwnerFullOrDjangoModelPermissions,
)

from marinerg_data_access.models import Dataset
from marinerg_data_access.serializers import DatasetSerializer


class DatasetPermissions(OwnerFullOrDjangoModelPermissions):
    owner_field = "creator"


class DatasetViewSet(SearchableModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        DatasetPermissions,
    ]

    ordering_fields = SearchableModelViewSet.ordering_fields
    ordering: tuple[str, ...] = ("created_at",)
    search_fields = ["title", "facility__name", "equipment__name"]

    def perform_create(self, serializer):
        serializer.save(creator=Member.objects.get(id=self.request.user.id))
