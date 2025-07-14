from unittest.mock import patch

import pytest

from streamfieldindex import indexer
from streamfieldindex.models import IndexEntry

# Define a mark for all tests in this file
pytestmark = pytest.mark.django_db


def test_basic_blocks(basic_blocks_page):
    indexer.index_page(basic_blocks_page)

    assert IndexEntry.objects.count() == 4
    assert IndexEntry.objects.get(block_name="heading").block_value == "This is a test char block"
    assert IndexEntry.objects.get(block_name="description").block_value == "This is a test text block"
    assert IndexEntry.objects.get(block_name="email").block_value == "nye.bevan@nhs.net"
    assert IndexEntry.objects.get(block_name="number").block_value == "123"


def test_richtext_block(richtext_block_page):
    indexer.index_page(richtext_block_page)

    assert IndexEntry.objects.count() == 1
    assert (
        IndexEntry.objects.get(block_name="paragraph").block_value == "<p>This is a test <em>richtext</em> block</p>"
    )


def test_list_block(list_block_page):
    indexer.index_page(list_block_page)

    # There should be 4 entries, 1 for the list block and 3 for the items inside the list
    assert IndexEntry.objects.count() == 4

    # The values are stored individually as separate items
    assert list(IndexEntry.objects.filter(block_name="numbers:item").values_list("block_value", flat=True)) == [
        "1",
        "2",
        "3",
    ]


def test_complex_list_block(complex_list_block_page):
    """Ensure list blocks also work when they have complex structural blocks as the child block"""
    indexer.index_page(complex_list_block_page)

    # 1 - The list block
    # 2 - Items inside the list
    # 2x3 - Sub blocks of the PersonBlock struct
    # 2x2 - Sub blocks if the PersonBlock.body streamblock
    # = 13 blocks in total
    assert IndexEntry.objects.count() == 13

    assert list(IndexEntry.objects.filter(block_name="name").values_list("block_value", flat=True)) == [
        "Kofoworola Abeni Pratt",
        "Benjamin Moore",
    ]
    assert list(IndexEntry.objects.filter(block_name="heading").values_list("block_value", flat=True)) == [
        "Career",
        "Career",
    ]

    # There are two items inside the list
    assert IndexEntry.objects.filter(block_name="people:item").count() == 2


def test_struct_block(struct_block_page):
    indexer.index_page(struct_block_page)

    assert IndexEntry.objects.count() == 4

    # struct blocks do not have value themselves
    assert IndexEntry.objects.get(block_name="person").block_value == ""

    # the struct block children have values instead
    assert IndexEntry.objects.get(block_name="name").block_value == "Aneurin Bevan"
    assert IndexEntry.objects.get(block_name="bio").block_value == "<p>Founder of the NHS</p>"


def test_stream_block(stream_block_page):
    indexer.index_page(stream_block_page)

    # stream blocks do not have value themselves
    assert IndexEntry.objects.get(block_name="stream").block_value == ""

    # the stream block children have values instead
    assert IndexEntry.objects.get(block_name="heading").block_value == "This is a test heading block"
    assert IndexEntry.objects.get(block_name="paragraph").block_value == "<p>This is a test paragraph block</p>"


def test_image_block(image, image_block_page):
    indexer.index_page(image_block_page)

    assert IndexEntry.objects.get(block_name="image").block_value == str(image.id)


def test_index_all_with_no_pages():
    indexer.index_all()
    assert IndexEntry.objects.count() == 0


def test_index_all(
        basic_blocks_page,
        richtext_block_page,
        list_block_page,
        complex_list_block_page,
        struct_block_page,
        stream_block_page,
        image_block_page
    ):
    indexer.index_all()
    assert IndexEntry.objects.count() == 30
    assert IndexEntry.objects.filter(page=basic_blocks_page).count() == 4
    assert IndexEntry.objects.filter(page=richtext_block_page).count() == 1
    assert IndexEntry.objects.filter(page=list_block_page).count() == 4
    assert IndexEntry.objects.filter(page=complex_list_block_page).count() == 13
    assert IndexEntry.objects.filter(page=struct_block_page).count() == 4
    assert IndexEntry.objects.filter(page=stream_block_page).count() == 3
    assert IndexEntry.objects.filter(page=image_block_page).count() == 1


@patch("streamfieldindex.indexer._collect_entries_for_field")
def test_batching(mock, many_pages):
    indexer.index_all()
    assert mock.call_count == 1000