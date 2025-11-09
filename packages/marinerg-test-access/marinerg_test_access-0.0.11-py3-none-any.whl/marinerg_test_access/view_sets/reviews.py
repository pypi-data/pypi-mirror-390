from rest_framework import permissions, viewsets

from marinerg_test_access.models import (
    FacilityTestReport,
    AccessApplicationFacilityReview,
    AccessApplicationBoardReview,
)

from marinerg_test_access.serializers import (
    FacilityTestReportSerializer,
    AccessApplicationFacilityReviewSerializer,
    AccessApplicationBoardReviewSerializer,
)


class FacilityTestReportViewSet(viewsets.ModelViewSet):
    queryset = FacilityTestReport.objects.all().order_by("id")
    serializer_class = FacilityTestReportSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class AccessApplicationFacilityReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessApplicationFacilityReview.objects.all().order_by("id")
    serializer_class = AccessApplicationFacilityReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class AccessApplicationBoardReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessApplicationBoardReview.objects.all().order_by("id")
    serializer_class = AccessApplicationBoardReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
