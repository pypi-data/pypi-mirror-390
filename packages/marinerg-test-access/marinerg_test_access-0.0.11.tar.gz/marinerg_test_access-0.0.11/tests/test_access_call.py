from django.utils import timezone

from ichec_django_core.models import Member

from ichec_django_core.utils.test_utils.test_client import (
    AuthAPITestCase,
    setup_default_users_and_groups,
)

from marinerg_test_access.utils.test_utils.test_client import setup_access_call


class AccessCallViewTests(AuthAPITestCase):

    template = {
        "title": "My Access Call",
        "description": "Description of my access call",
        "coordinator": "",
        "board_chair": "",
        "board_members": [],
        "closing_date": str(timezone.now()),
        "form": {
            "groups": [
                {
                    "fields": [
                        {
                            "label": "Requires Support",
                            "key": "requires_support",
                            "description": "Do you require facility support?",
                            "field_type": "BOOLEAN",
                        }
                    ]
                }
            ]
        },
    }

    update_template = {"description": "Modified description of my access call"}

    def setUp(self):
        self.url = "/api/access_calls/"

        setup_default_users_and_groups()

        setup_access_call()

    def get_user(self, name: str) -> Member:
        return Member.objects.get(username=name)

    def get_user_url(self, name: str):
        return f"http://testserver/api/members/{self.get_user(name).id}/"

    def get_template(self, username: str = "admin_user") -> dict:
        template = self.template
        template["coordinator"] = self.get_user_url(username)
        template["board_chair"] = self.get_user_url(username)
        return template

    def check_response(self, returned, expected, skip_keys: tuple = ()):
        for key, expected_value in expected.items():

            if key in skip_keys:
                continue

            returned_value = returned[key]
            if isinstance(expected_value, dict):
                self.compare_dicts(returned_value, expected_value, skip_keys)
            elif isinstance(expected_value, list):
                self.assertEqual(len(expected_value), len(returned_value))
            else:
                self.assertEqual(returned_value, expected_value)

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_regular_user(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_regular_user(self):
        self.assert_200(self.authenticated_detail("regular_user", 1))

    def test_create_not_authenticated(self):
        self.assert_401(self.create(self.get_template()))

    def test_create_regular_user(self):
        self.assert_403(self.authenticated_create("regular_user", self.get_template()))

    def test_create_consortium_admin(self):
        response = self.assert_201(
            self.authenticated_create("admin_user", self.get_template())
        )
        # self.check_response(response, self.get_template(), ("closing_date"))

    def xtest_update_consortium_admin(self):
        created = self.assert_201(
            self.authenticated_create("admin_user", self.get_template())
        )

        for key, value in self.update_template.items():
            created[key] = value

        created["application_fields"] = [
            f["url"] for f in created["application_fields"]
        ]
        updated = self.assert_200(
            self.authenticated_update("admin_user", created["id"], created)
        )
