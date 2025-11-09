from django.db import models
from django.utils import timezone

from ichec_django_core.models import Member, TimesStampMixin, PopulatedForm

from marinerg_facility.models import Facility

from .access_call import AccessCall
from .summary import generate_summary


class AccessApplication(TimesStampMixin):

    class Meta:
        verbose_name = "Access Application"
        verbose_name_plural = "Access Application"

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        SUBMITTED = "SUBMITTED", "Submitted"
        AWAITING_FACILITY_REVIEW = "FACILITY", "Awaiting Facility Review"
        AWAITING_BOARD_REVIEW = "BOARD", "Awaiting Board Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    facilities = models.ManyToManyField(
        Facility, related_name="application_choices", blank=True
    )

    chosen_facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="applications", null=True
    )

    request_start_date = models.DateTimeField(null=True)
    request_end_date = models.DateTimeField(null=True)
    dates_flexible = models.BooleanField(default=False)

    applicant = models.ForeignKey(Member, on_delete=models.CASCADE)
    call = models.ForeignKey(AccessCall, on_delete=models.CASCADE)

    summary = models.FileField(null=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.CREATED
    )

    form = models.OneToOneField(PopulatedForm, on_delete=models.CASCADE)

    submitted = models.DateTimeField(null=True)
    __last_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__last_status = str(self.status)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        if (
            str(self.status).lower() == "submitted"
            and self.__last_status.lower() == "created"
        ):
            self.submitted = timezone.now()
            generate_summary(self)
            self.status = "FACILITY"
        self.__last_status = str(self.status)

        super().save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return f"{self.applicant.email} application for '{self.call.title}'"

    @property
    def summary_url(self):
        return "summary" if self.summary else ""
