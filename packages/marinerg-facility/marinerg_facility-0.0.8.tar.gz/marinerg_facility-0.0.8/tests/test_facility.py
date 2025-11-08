import tempfile
import json

from rest_framework import status
from django.contrib.auth.models import User

from ichec_django_core.models import Address
from marinerg_facility.models import Facility

from ichec_django_core.utils.test_utils.test_client import (
    AuthAPITestCase,
    setup_default_users_and_groups,
    add_group_permissions,
    generate_image,
)


class TestFacilityViewTests(AuthAPITestCase):

    template = {
        "name": "My Facility",
        "acronym": "MF",
        "description": "Description of the facility",
        "address": {"line1": "1234 Street", "region": "Region", "country": "IE"},
        "website": "www.facility.org",
    }

    template_updates = {"name": "My Facility Edited"}

    def setUp(self):
        self.url = "/api/facilities/"
        setup_default_users_and_groups()

        add_group_permissions(
            "admins",
            Facility,
            ["change_facility", "add_facility"],
        )

        add_group_permissions(
            "admins",
            Address,
            ["change_address", "add_address"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_create_not_authenticated(self):
        self.assert_401(self.create(self.template))

    def test_create_authenticated_no_permission(self):
        self.assert_403(self.authenticated_create("regular_user", self.template))

    def test_create_authenticated_permission(self):
        self.assert_201(self.authenticated_create("admin_user", self.template))

    def test_create_with_image_authenticated_permission(self):
        image = generate_image()
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
        image.save(tmp_file, format="PNG")

        tmp_file.seek(0)

        response = self.authenticated_create("admin_user", self.template)
        self.assert_201(response)

        resource_id = json.loads(response.content)["id"]
        self.assert_204(
            self.authenticated_put_file(
                "admin_user",
                resource_id,
                "image",
                {"file": tmp_file},
                "test_image.png",
            )
        )
