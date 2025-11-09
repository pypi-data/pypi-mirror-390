from datetime import datetime

from ichec_django_core.utils.test_utils.models import (
    MemberDetail,
    FormCreate,
    FormGroupCreate,
    FormFieldCreate,
    PopulatedFormCreate,
    FormFieldValueCreate,
)

from marinerg_facility.utils.test_utils.models import FacilityDetail

from .models import (
    AccessCallCreate,
    AccessCallDetail,
    AccessApplicationCreate,
)


def create_access_calls(
    count: int = 10,
    offset: int = 0,
    members: tuple[MemberDetail, ...] = (),
    selectable_facilities: tuple[FacilityDetail, ...] = (),
) -> list[AccessCallCreate]:

    contents = []
    for idx in range(offset, count + offset):
        fields = [
            FormFieldCreate(
                label="Support Needed?",
                key="support_needed",
                field_type="BOOLEAN",
                required=False,
                default="false",
                description="Do you need support?",
            ),
            FormFieldCreate(
                label="Description of Device",
                key="description",
                field_type="TEXT",
                required=True,
                default="",
                description="Give a detailed description of the device",
            ),
        ]

        groups = [FormGroupCreate(fields=fields)]

        contents.append(
            AccessCallCreate(
                title=f"Access Call {idx}",
                description=f"Description of Access Call {idx}",
                status="OPEN",
                closing_date=datetime.now(),
                coordinator=members[0].url,
                board_chair=members[1].url,
                board_members=[members[2].url, members[3].url, members[4].url],
                selectable_facilities=[f.url for f in selectable_facilities],
                form=FormCreate(groups=groups),
            )
        )
    return contents


def create_applications(call: AccessCallDetail, count: int = 10, offset: int = 0):

    description_field = call.get_field("description")
    if not description_field:
        raise RuntimeError("Field not found")

    contents = []
    for idx in range(offset, count + offset):
        contents.append(
            AccessApplicationCreate(
                call=call.url,
                form=PopulatedFormCreate(
                    values=[
                        FormFieldValueCreate(
                            field=description_field.id, value="description"
                        )
                    ]
                ),
            )
        )
    return contents
