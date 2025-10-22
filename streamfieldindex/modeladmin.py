from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from wagtail_modeladmin.helpers import PermissionHelper
from wagtail_modeladmin.options import ModelAdmin

from .models import IndexEntry


class IndexEntryPermissionHelper(PermissionHelper):
    """
    PermissionsHelper for a read-only modeladmin
    """

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_inspect_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False

    def user_can_create(self, user):
        return False


class IndexEntryAdmin(ModelAdmin):
    model = IndexEntry
    permission_helper_class = IndexEntryPermissionHelper
    menu_icon = "list-ul"
    menu_label = "Streamfield Index"

    list_display = ("block_name", "block_path", "truncated_block_value", "page_link")
    list_filter = ("block_name",)
    search_fields = ("block_name", "block_path", "block_value")

    def page_link(self, instance):
        edit_url = reverse("wagtailadmin_pages:edit", args=[instance.page.id])
        return format_html(f'<a href="{edit_url}">{instance.page}</a>')

    page_link.short_description = "Page"

    def truncated_block_value(self, instance):
        return truncatechars(instance.block_value, 100)

    truncated_block_value.short_description = "Block Value"
