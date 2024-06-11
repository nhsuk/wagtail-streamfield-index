from wagtail import hooks
from wagtail.signals import page_published, page_unpublished, post_page_move

from .indexer import index_page


@hooks.register("after_create_page")
def index_after_create_page(request, page):
    index_page(page)


@hooks.register("after_edit_page")
def index_after_edit_page(request, page):
    index_page(page)


@hooks.register("after_copy_page")
def index_after_copy_page(request, page):
    index_page(page)


def post_publish(sender, instance, **kwargs):
    index_page(instance)


def index_post_page_move(sender, instance, **kwargs):
    index_page(instance)


def index_post_unpublished(sender, instance, **kwargs):
    index_page(instance)


page_published.connect(post_publish)
page_unpublished.connect(index_post_unpublished)
post_page_move.connect(index_post_page_move)
