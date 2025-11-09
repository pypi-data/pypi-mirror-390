from rest_framework import permissions, viewsets

from ichec_django_core.view_sets import (
    SearchableModelViewSet,
    ObjectFileDownloadView,
    OwnerFullOrDjangoModelPermissions,
)

from marinerg_test_access.models import AccessCall, AccessCallFacilityReview
from marinerg_test_access.serializers import (
    AccessCallListSerializer,
    AccessCallDetailSerializer,
    AccessCallCreateSerializer,
    AccessCallFacilityReviewSerializer,
)


class CoordinatorEditOrDjangoModelPermissions(OwnerFullOrDjangoModelPermissions):
    owner_field = "coordinator"


class AccessCallViewSet(SearchableModelViewSet):
    queryset = AccessCall.objects.all()
    serializer_class = AccessCallListSerializer

    serializers = {
        "retrieve": AccessCallDetailSerializer,
        "list": AccessCallListSerializer,
        "create": AccessCallCreateSerializer,
        "update": AccessCallListSerializer,
        "partial_update": AccessCallListSerializer,
    }

    permission_classes = [
        permissions.IsAuthenticated,
        CoordinatorEditOrDjangoModelPermissions,
    ]

    ordering_fields = ("status",)
    ordering: tuple[str, ...] = ("created_at",)
    search_fields = ["title"]


class ApplicationSummaryDownloadView(ObjectFileDownloadView):
    model = AccessCall
    file_field = "applications_summary"
    permissions_class = CoordinatorEditOrDjangoModelPermissions


class AccessCallFacilityReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessCallFacilityReview.objects.all().order_by("id")
    serializer_class = AccessCallFacilityReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
