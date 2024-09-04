from django.urls import reverse
from wagtail import hooks
from wagtail.admin.admin_url_finder import ModelAdminURLFinder, register_admin_url_finder
from wagtail.signals import page_published, page_unpublished, post_page_move

from .indexer import clear_index, index_page
from .models import IndexEntry


@hooks.register("after_create_page")
def index_after_create_page(request, page):
    index_page(page)


@hooks.register("after_edit_page")
def index_after_edit_page(request, page):
    index_page(page)


@hooks.register("after_copy_page")
def index_after_copy_page(request, page, new_page):
    index_page(new_page)


def index_unpublished(sender, instance, **kwargs):
    clear_index(instance)


def post_publish(sender, instance, **kwargs):
    index_page(instance)


def index_post_page_move(sender, instance, **kwargs):
    index_page(instance)


class IndexEntryAdminURLFinder(ModelAdminURLFinder):
    """
    Custom URL finder for IndexEntry model
    https://github.com/gasman/wagtail/blob/9174db40746514b6fa6d792b25507571381c9255/wagtail/admin/admin_url_finder.py#L28
    """

    def construct_edit_url(self, instance):
        return reverse("wagtailadmin_pages:edit", args=[instance.page.id])


register_admin_url_finder(IndexEntry, IndexEntryAdminURLFinder)

page_published.connect(post_publish)
page_unpublished.connect(index_unpublished)
post_page_move.connect(index_post_page_move)
