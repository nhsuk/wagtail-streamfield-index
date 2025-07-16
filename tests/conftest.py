import io
import json
from uuid import uuid4

import pytest
from django.core.files.images import ImageFile
from PIL import Image
from wagtail.blocks.stream_block import StreamValue
from wagtail.images import get_image_model
from wagtail.models import Page

from .testapp.models import HomePage

MANY = 1000


@pytest.fixture
def root_page():
    return Page.objects.get(slug="root", depth=1)


def create_page(parent_page, stream_data):
    """Create a valid page by saving data to a real page model and getting it back out of the database"""
    stream_block = HomePage.body.field.stream_block
    test_page = HomePage(
        body=StreamValue(stream_block, [], is_lazy=True, raw_text=json.dumps(stream_data)),
        title="Home Page",
        slug=uuid4(),
    )
    parent_page.add_child(instance=test_page)
    test_page.refresh_from_db()
    return test_page


@pytest.fixture
def image():
    image = Image.new("RGBA", size=(50, 50), color=(0, 70, 177))
    image_file = io.BytesIO()
    image.save(image_file, "png")  # or whatever format you prefer
    file = ImageFile(image_file, name="testimage.png")
    wagtail_image = get_image_model()(file=file, title="My Test Image")
    wagtail_image.save()
    return wagtail_image


@pytest.fixture
def many_pages(root_page):
    for _ in range(MANY - 1):
        create_page(root_page, [{"type": "heading", "value": "This is a test char block"}])
    return create_page(root_page, [{"type": "heading", "value": "This is a test char block"}])


@pytest.fixture
def basic_blocks_page(root_page):
    return create_page(
        root_page,
        [
            {"type": "heading", "value": "This is a test char block"},
            {"type": "description", "value": "This is a test text block"},
            {"type": "email", "value": "nye.bevan@nhs.net"},
            {"type": "number", "value": 123},
        ],
    )


@pytest.fixture
def richtext_block_page(root_page):
    return create_page(root_page, [{"type": "paragraph", "value": "<p>This is a test <em>richtext</em> block</p>"}])


@pytest.fixture
def list_block_page(root_page):
    return create_page(root_page, [{"type": "numbers", "value": [1, 2, 3]}])


@pytest.fixture
def complex_list_block_page(root_page):
    """Ensure list blocks also work when they have complex structural blocks as the child block"""
    complex_list_block_data = {
        "type": "people",
        "value": [
            {
                "name": "Kofoworola Abeni Pratt",
                "bio": "<p>The first black nurse to work in the NHS</p>",
                "body": [
                    {"type": "heading", "value": "Career"},
                    {
                        "type": "paragraph",
                        "value": "<p>She became vice-president of the International Council of Nurses and the first black Chief Nursing Officer of Nigeria, working in the Federal Ministry of Health.</p>",
                    },
                ],
            },
            {
                "name": "Benjamin Moore",
                "bio": "<p>Credited with the first use of the words National Health Service.</p>",
                "body": [
                    {"type": "heading", "value": "Career"},
                    {
                        "type": "paragraph",
                        "value": "<p>He held the first chair of biochemistry in the UK, and founded the Biochemical Journal, one of the earliest academic journals in the subject.</p>",
                    },
                ],
            },
        ],
    }
    return create_page(root_page, [complex_list_block_data])


@pytest.fixture
def struct_block_page(root_page):
    struct_block_data = {
        "type": "person",
        "value": {
            "name": "Aneurin Bevan",
            "bio": "<p>Founder of the NHS</p>",
            "body": [],
        },
    }
    return create_page(root_page, [struct_block_data])


@pytest.fixture
def stream_block_page(root_page):
    stream_block_data = {
        "type": "stream",
        "value": [
            {
                "type": "heading",
                "value": "This is a test heading block",
            },
            {
                "type": "paragraph",
                "value": "<p>This is a test paragraph block</p>",
            },
        ],
    }
    return create_page(root_page, [stream_block_data])


@pytest.fixture
def image_block_page(image, root_page):
    return create_page(root_page, [{"type": "image", "value": image.id}])
