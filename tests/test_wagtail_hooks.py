import pytest
from django.urls import reverse
from wagtail.tests.utils import WagtailTestUtils
from wagtail.test.utils.wagtail_factories import PageFactory

import streamfieldindex
from streamfieldindex.wagtail_hooks import IndexEntryAdminURLFinder


@pytest.mark.django_db
class TestIndexEntryAdminURLFinder(WagtailTestUtils):

    def test_construct_edit_url(self):
        finder = IndexEntryAdminURLFinder()
        instance = streamfieldindex.models.IndexEntry(page=PageFactory(), block_type="text", block_value="Hello, world!", block_path="content",)
        expected_url = reverse("wagtailadmin_pages:edit", args=[instance.page.id])
        assert finder.construct_edit_url(instance) == expected_url