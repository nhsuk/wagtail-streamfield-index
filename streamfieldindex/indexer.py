import logging
import time
from django.db import transaction
from wagtail.blocks import StreamValue, StructValue
from wagtail.fields import StreamField
from wagtail.models import Page

from .iterator import flatten_streamfield
from .models import BlockTypes, IndexEntry

logger = logging.getLogger(__name__)


def index_all(page_query=None, batch_size=100):
    """
    Loop through all pages and save an index entry for each streamblock we find.
    """
    start_time = time.time()

    if page_query is None:
        page_query = Page.objects.live().all()

    total_pages = page_query.count()
    logger.info(f"Found {total_pages} pages to index")

    for offset in range(0, total_pages, batch_size):
        end_offset = min(offset + batch_size, total_pages)
        logger.info(f"Processing batch of pages from {offset} to {end_offset}")

        with transaction.atomic():
            # Get the specific pages for this batch
            batch_pages = list(page_query.specific()[offset:end_offset])

            # Batch delete existing entries
            page_ids = [page.id for page in batch_pages]
            if page_ids:
                IndexEntry.objects.filter(page__id__in=page_ids).delete()

            # Collect all entries to create
            entries_to_create = []
            for page in batch_pages:
                for field in page._meta.fields:
                    if not isinstance(field, StreamField):
                        continue
                    # Collect entries for this field
                    entries_to_create.extend(_collect_entries_for_field(field, page))

            # Bulk create entries in sub-batches to avoid memory issues
            if entries_to_create:
                for i in range(0, len(entries_to_create), 1000):
                    IndexEntry.objects.bulk_create(entries_to_create[i : i + 1000])

        elapsed_time = time.time() - start_time
        logger.debug(f"Time elapsed {elapsed_time:.2f} seconds")

    elapsed_time = time.time() - start_time
    logger.info(f"Completed indexing all pages. Elapsed time: {elapsed_time:.2f} seconds")


def _collect_entries_for_field(field, page):
    """Helper function to collect IndexEntry objects without saving them."""
    entries = []
    field_name = field.name
    streamvalue = getattr(page, field_name)

    for block, path in flatten_streamfield(streamvalue):
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

        entries.append(
            IndexEntry(
                block_name=block_name,
                block_type=block_type,
                block_value=block_value,
                block_path=block_path,
                page=page,
                field_name=field_name,
            )
        )

    return entries


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
