# wagtail-streamfield-index

Indexing of streamfield data in Wagtail

## Installation

Install the package
```sh
pip install wagtail-streamfield-index
```

Add to your installed apps

```py
INSTALLED_APPS = [
    ...
    "streamfieldindex",
    ...
]
```

Run `python manage.py streamfieldindex` to index all pages.

After indexing, your database will contain one `IndexEntry` for every block found in a page model.

The index will keep itself up-to-date every time a page is saved.

#### ModelAdmin

If you would like to see a list of indexed blocks in your wagtail admin interface, you can register the [modeladmin](https://docs.wagtail.io/en/latest/reference/contrib/modeladmin/index.html)

Make sure modeladmin app is installed:
```py
INSTALLED_APPS = [
    ...
    "wagtail_modeladmin",
    ...
]
```

Register the `IndexEntryAdmin` in a wagtail_hooks.py file:
```py
from wagtail_modeladmin.options import modeladmin_register
from streamfieldindex.modeladmin import IndexEntryAdmin

modeladmin_register(IndexEntryAdmin)
```


#### IndexEntry model

`from streamfieldindex.models import IndexEntry`

##### Fields

`block_name`
The name that you gave to your block in the streamfield definition.
e.g "author" or "heading" in the following example:
```py
my_field = StreamField([
    ('author', AuthorBlock()),
    ('heading', CharBlock()),
    use_json_field=True
])
```

For items inside list blocks, the `block_name` is set to the list block name with ":item" appended, since individual items inside a list block do not have a name.

`block_value`
The string value of the block, in the form that it is stored in the streamfield. `StructBlock`, `StreamBlock` and `ListBlock`s have an empty string as the block_value since you can inspect the contents of those blocks by looking at their sub-blocks.
If you have a complex block type such as an ImageChooser block, see the `get_bound_block()` method

`block_path`
A slash-delimited path to the location of the block within the streamfield.
E.g. if block_path = `5/author/title`

1. `5`. The 6th block in the streamfield.
2. `author`. The 6th block is named `author`.
3. `title`. The `title` sub-block of `author`.

`field_name`
The name of the field where the block was found.

`page`
The page where the block was found.

##### Methods

`get_bound_block()`
Returns a Wagtail `BoundBlock` instance of the block. See the [Wagtail docs](https://docs.wagtail.io/en/v2.0/topics/streamfield.html#boundblocks-and-values) for explaination of `BoundBlock`s.

##### Example usage

If you had an `author` block and wanted to find all usage of that block:

```py
from streamfieldindex.models import IndexEntry

for index_entry in IndexEntry.objects.filter(block_name="author"):
    print(index_entry.page.id) # Print the page ID where the block is found
    print(index_entry.field_name) # Print the field where the block is found
    print(index_entry.block_path) # Print a slash-separated path to the block inside the field
```

## Contributing

### Getting started

1. Clone the repo `git clone https://github.com/nhsuk/wagtail-streamfield-index.git`
2. Install dependencies `pip install .[testing,linting]`

If you are having issues in installing, it may be of use to use an environment tool 
like [virtualenv](https://docs.python.org/3/library/venv.html)

### Formatting

`black .`

### Linting

`flake8 .`

### Tests

`pytest`
