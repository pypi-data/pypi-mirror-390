from django.utils import timezone

from ichec_django_core.models import Member, Form, PopulatedForm

from ichec_django_core.utils.test_utils.test_client import add_group_permissions

from marinerg_test_access.models import AccessCall, AccessApplication


def setup_access_call():

    coordinator = Member.objects.create(username="access_call_coordinator")
    access_call_board_member = Member.objects.create(
        username="access_call_board_member"
    )

    form = Form.objects.create()

    access_call = AccessCall.objects.create(
        title="Test access call",
        description="Description of access call",
        status="OPEN",
        closing_date=timezone.now(),
        coordinator=coordinator,
        board_chair=access_call_board_member,
        form=form,
    )

    access_call.board_members.set([access_call_board_member])

    add_group_permissions("admins", AccessCall, ["change_accesscall", "add_accesscall"])
    return access_call


def setup_application(call, applicant="test_applicant"):

    form = PopulatedForm.objects.create()
    applicant = Member.objects.create(username=applicant)
    AccessApplication.objects.create(applicant=applicant, call=call, form=form)
