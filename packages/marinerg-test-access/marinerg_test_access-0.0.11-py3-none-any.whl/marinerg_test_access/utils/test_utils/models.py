from datetime import datetime

from pydantic import BaseModel
from ichec_django_core.utils.test_utils.models import (
    Identifiable,
    Timestamped,
    FormCreate,
    FormDetail,
    FormFieldDetail,
    register_types,
    PopulatedFormCreate,
    PopulatedFormDetail,
)


class AccessCallBase(BaseModel, frozen=True):

    title: str
    description: str
    status: str
    closing_date: datetime
    coordinator: str
    board_chair: str
    board_members: list[str] = []
    selectable_facilities: list[str] = []


class AccessCallCreate(AccessCallBase, frozen=True):

    form: FormCreate


class AccessCallDetail(Timestamped, AccessCallBase, frozen=True):

    form: FormDetail

    def get_field(self, key: str) -> FormFieldDetail | None:
        for group in self.form.groups:
            for field in group.fields:
                if field.key == key:
                    return field
        return None


class AccessCallList(Timestamped, AccessCallBase, frozen=True):

    pass


class ApplicationFieldValueBase(BaseModel, frozen=True):

    value: str
    field: str
    asset: str | None = None


class ApplicationFieldValueCreate(ApplicationFieldValueBase, frozen=True):
    pass


class ApplicationFieldValueDetail(Identifiable, ApplicationFieldValueBase, frozen=True):
    pass


class AccessApplicationBase(BaseModel, frozen=True):
    call: str
    facilities: list[str] = []
    chosen_facility: str | None = None
    request_start_date: datetime | None = None
    request_end_date: datetime | None = None
    dates_flexible: bool = True
    status: str = "SUBMITTED"


class AccessApplicationCreate(AccessApplicationBase, frozen=True):
    form: PopulatedFormCreate


class AccessApplicationDetail(Timestamped, AccessApplicationBase, frozen=True):
    applicant: str
    submitted: datetime | None = None
    form: PopulatedFormDetail


register_types(
    "access_calls",
    {"create": AccessCallCreate, "detail": AccessCallDetail, "list": AccessCallList},
)

register_types(
    "access_applications",
    {"create": AccessApplicationCreate, "detail": AccessApplicationDetail},
)
