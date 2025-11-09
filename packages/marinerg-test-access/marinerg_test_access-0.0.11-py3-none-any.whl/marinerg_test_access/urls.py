from django.urls import path

from .view_sets import (
    AccessApplicationViewSet,
    SafetyStatementDownloadView,
    SummaryDownloadView,
    SafetyStatementUploadView,
    AccessCallViewSet,
    ApplicationSummaryDownloadView,
    AccessCallFacilityReviewViewSet,
    AccessApplicationFacilityReviewViewSet,
    AccessApplicationBoardReviewViewSet,
    FacilityTestReportViewSet,
)


def register_drf_views(router):
    router.register(r"access_calls", AccessCallViewSet)
    router.register(r"access_call_facility_reviews", AccessCallFacilityReviewViewSet)
    router.register(r"access_applications", AccessApplicationViewSet)
    router.register(
        r"access_application_facility_reviews", AccessApplicationFacilityReviewViewSet
    )
    router.register(
        r"access_application_board_reviews", AccessApplicationBoardReviewViewSet
    )
    router.register(r"facility_test_reports", FacilityTestReportViewSet)


urlpatterns = [
    path(
        r"access_calls/<int:pk>/application_summary",
        ApplicationSummaryDownloadView.as_view(),
        name="application_summaries",
    ),
    path(
        r"access_applications/<int:pk>/safety_statement",
        SafetyStatementDownloadView.as_view(),
        name="safety_statements",
    ),
    path(
        r"access_applications/<int:pk>/summary",
        SummaryDownloadView.as_view(),
        name="summaries",
    ),
    path(
        r"access_applications/<int:pk>/safety_statement/upload",
        SafetyStatementUploadView.as_view(),
        name="safety_statements_upload",
    ),
]
