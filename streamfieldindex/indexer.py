from wagtail.blocks import StreamValue, StructValue
from wagtail.fields import StreamField
from wagtail.models import Page

from .iterator import flatten_streamfield
from .models import BlockTypes, IndexEntry


def index_all(page_query=None):
    """
    Loop through all pages and save an index entry for each streamblock we find.
    """

    if page_query is None:
        page_query = Page.objects.live().all()

    for page in page_query.specific():
        index_page(page)


def clear_index(page):
    IndexEntry.objects.filter(page__id=page.id).delete()


def index_page(page):

    # Clear the index for this specific page
    IndexEntry.objects.filter(page__id=page.id).delete()

    if page.live:  # we dont want to index any draft/unpublished pages
        for field in page._meta.fields:
            if not isinstance(field, StreamField):
                # We are only interested in streamfields. Skip over non-streamfield fields
                continue

            index_field(field, page)


def index_field(field, page):

    field_name = field.name
    streamvalue = getattr(page, field_name)
    for block, path in flatten_streamfield(streamvalue):
        field_name = field_name
        block_name = path[-1]

        if isinstance(block.value, StructValue):
            block_value = ""
            block_type = BlockTypes.STRUCT
        elif isinstance(block.value, StreamValue):
            block_value = ""
            block_type = BlockTypes.STREAM
        elif isinstance(block.value, list):
            block_value = ""
            block_type = BlockTypes.LIST
        else:
            block_value = block.block.get_prep_value(block.value)
            if block_value is None:
                block_value = ""
            block_type = BlockTypes.OTHER

        # If the block_name is an integer, we are dealing with an item inside a list
        try:
            int(block_name)
            block_name = path[-2] + ":item"
        except ValueError:
            pass

        block_path = "/".join(path)

        entry = IndexEntry(
            block_name=block_name,
            block_type=block_type,
            block_value=block_value,
            block_path=block_path,
            page=page,
            field_name=field_name,
        )
        entry.save()
